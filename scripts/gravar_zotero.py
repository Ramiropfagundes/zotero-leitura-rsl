# Cria destaques (annotations) no PDF e uma nota de leitura por artigo no Zotero via API web
# Uso: python gravar_zotero.py leitura_localizada.json registro.json [--forcar]
import json, os, sys, html, urllib.request

sys.stdout.reconfigure(encoding='utf-8')

PALETA = [('#ffd400', 'amarelo'), ('#5fb236', 'verde'), ('#2ea8e5', 'azul'), ('#ff6666', 'vermelho'),
          ('#a28ae5', 'roxo'), ('#e56eee', 'magenta'), ('#f19837', 'laranja'), ('#aaaaaa', 'cinza')]


def cores_por_pergunta(leitura):
    return {q: PALETA[i % len(PALETA)] for i, q in enumerate(leitura['perguntas'])}


def variavel(nome):
    # Primeiro o ambiente do processo; no Windows, também o registro (variável de usuário
    # criada depois de o terminal/VS Code ter sido aberto ainda não aparece no ambiente)
    valor = os.environ.get(nome)
    if not valor and sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as k:
                valor = winreg.QueryValueEx(k, nome)[0]
        except OSError:
            pass
    if not valor:
        raise SystemExit(f'Variável de ambiente {nome} não definida: ver README.md da skill')
    return valor.strip()


def chave_api():
    return variavel('ZOTERO_API_KEY')


def api(path, key, dados=None):
    req = urllib.request.Request(
        f"https://api.zotero.org/users/{variavel('ZOTERO_USER_ID')}{path}",
        data=json.dumps(dados).encode('utf-8') if dados is not None else None,
        headers={'Zotero-API-Key': key, 'Zotero-API-Version': '3', 'Content-Type': 'application/json'},
        method='POST' if dados is not None else 'GET')
    return json.load(urllib.request.urlopen(req))


def post(itens, key):
    keys = []
    for i in range(0, len(itens), 50):  # limite da API: 50 itens por requisição
        lote = itens[i:i + 50]
        r = api('/items', key, lote)
        if r.get('failed'):
            raise SystemExit(f'Falhou: {r["failed"]}')
        keys += [r['successful'][str(j)]['key'] for j in range(len(lote))]
    return keys


def main():
    leitura = json.load(open(sys.argv[1], encoding='utf-8'))
    forcar = '--forcar' in sys.argv
    key = chave_api()
    perguntas = leitura['perguntas']
    cores = cores_por_pergunta(leitura)
    colecao, data = leitura['colecao'], leitura['data']
    tag_col = f'RSL-{colecao}'
    registro = {}
    for nome, art in leitura['artigos'].items():
        nota_id = f"RSL-{colecao}-{art['id']}"
        # Evita duplicar: procura nota com o mesmo ID no item
        filhos = api(f"/items/{art['item']}/children", key)
        if any(nota_id in f['data'].get('note', '') for f in filhos) and not forcar:
            print(f'{nome}: já existe nota {nota_id}; pulado (use --forcar para gravar de novo)')
            continue
        att, quotes = art['attachment'], art['localizados']
        anns = [{
            'itemType': 'annotation', 'parentItem': att, 'annotationType': 'highlight',
            'annotationText': a['text'],
            'annotationComment': f"{a['q']} – {perguntas[a['q']]} [{art['cite']}]",
            'annotationColor': cores[a['q']][0], 'annotationPageLabel': a['label'],
            'annotationSortIndex': f"{a['page']:05d}|{a['offset']:06d}|{int(a['top']):05d}",
            'annotationPosition': json.dumps({'pageIndex': a['page'], 'rects': a['rects']}),
            'tags': [{'tag': f"RSL-{a['q']}"}, {'tag': tag_col}, {'tag': 'claude'}],
        } for a in quotes]
        keys = post(anns, key)

        parts = [f"<h1>RSL {html.escape(colecao)} – Leitura: {html.escape(art['cite'])}</h1>",
                 '<p><b>Rastreabilidade</b></p><ul>',
                 f"<li><b>Artigo:</b> {html.escape(art['reference'])}</li>"]
        if art.get('doi'):
            parts.append(f"<li><b>DOI:</b> <a href=\"https://doi.org/{art['doi']}\">{art['doi']}</a></li>")
        parts += [f"<li><b>Zotero:</b> item <a href=\"zotero://select/library/items/{art['item']}\">{art['item']}</a> · "
                  f"PDF <a href=\"zotero://open-pdf/library/items/{att}\">{att}</a> · coleção {html.escape(colecao)}"
                  f" ({leitura.get('colecao_key', '')})</li>",
                  f"<li><b>ID da nota:</b> {nota_id} · gerada por Claude em {data} a partir do texto do PDF</li>",
                  '<li><b>Cores no PDF:</b> ' + ' · '.join(f"{q} = {c[1]}" for q, c in cores.items()) +
                  ' (filtrar pelas tags RSL-Q…)</li></ul>',
                  '<p><i>Páginas: número impresso no artigo; entre parênteses, a página do PDF.</i></p>']
        for q, texto in perguntas.items():
            parts.append(f"<h2>{q}. {html.escape(texto)}</h2>")
            parts += [f"<p>{p}</p>" for p in art['answers'][q]]
            ev = [(a, k) for a, k in zip(quotes, keys) if a['q'] == q]
            if ev:
                parts.append(f"<p><b>Evidências no texto ({cores[q][1]}):</b></p><ul>")
                for a, k in ev:
                    link = f"zotero://open-pdf/library/items/{att}?page={a['page'] + 1}&amp;annotation={k}"
                    parts.append(f"<li>“{html.escape(a['text'])}” — <a href=\"{link}\">p. {a['label']} (PDF p. {a['page'] + 1})</a></li>")
                parts.append('</ul>')
        nota = {'itemType': 'note', 'parentItem': art['item'], 'note': '\n'.join(parts),
                'tags': [{'tag': tag_col}, {'tag': 'nota-leitura-claude'}]}
        nkey = post([nota], key)[0]
        registro[nome] = {'nota': nkey, 'destaques': keys}
        print(f'{nome}: nota {nkey} | {len(keys)} destaques')
    json.dump(registro, open(sys.argv[2], 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
