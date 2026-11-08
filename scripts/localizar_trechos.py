# Localiza cada trecho citado no PDF e acrescenta os retângulos (coordenadas Zotero) ao JSON da leitura
# Uso: python localizar_trechos.py leitura.json leitura_localizada.json
import json, sys, unicodedata
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    return ''.join(ch.lower() for ch in s if ch.isalnum())


def locate(page, quote):
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
    stream, owner = [], []
    for wi, w in enumerate(words):
        for ch in norm(w[4]):
            stream.append(ch)
            owner.append(wi)
    stream = ''.join(stream)
    q = norm(quote)
    pos = stream.find(q)
    if pos < 0:
        return None, 'não encontrado na página'
    if stream.find(q, pos + 1) >= 0:
        return None, 'aparece mais de uma vez; use um trecho mais longo'
    lines = {}
    for wi in sorted(set(owner[pos:pos + len(q)])):
        w = words[wi]
        r = lines.setdefault((w[5], w[6]), [w[0], w[1], w[2], w[3]])
        r[0] = min(r[0], w[0]); r[1] = min(r[1], w[1])
        r[2] = max(r[2], w[2]); r[3] = max(r[3], w[3])
    rects = sorted(lines.values(), key=lambda r: (r[1], r[0]))
    # As palavras vêm no espaço da página sem rotação (origem em cima); o Zotero usa o espaço
    # do PDF (origem embaixo, com o deslocamento da cropbox): converter pela matriz inversa
    inv = ~page.transformation_matrix
    zrects = []
    for r in rects:
        u = pymupdf.Rect(r) * inv
        zrects.append([round(u.x0, 3), round(u.y0, 3), round(u.x1, 3), round(u.y1, 3)])
    return zrects, (pos, rects[0][1])


leitura = json.load(open(sys.argv[1], encoding='utf-8'))
falhas = 0
for nome, art in leitura['artigos'].items():
    doc = pymupdf.open(art['pdf'])
    localizados = []
    for q, pi, text in art['quotes']:
        if doc[pi].rotation:
            print(f'AVISO {nome} pageIndex {pi}: página girada {doc[pi].rotation}°; conferir esse destaque no Zotero')
        rects, info = locate(doc[pi], text)
        if not rects:
            falhas += 1
            print(f'FALHOU {nome} {q} pageIndex {pi}: {info}: {text[:70]!r}')
            continue
        rotulo = doc[pi].get_label() or str(pi + art.get('first_page', 1))
        localizados.append(dict(q=q, page=pi, label=rotulo, text=text, rects=rects, offset=info[0], top=info[1]))
    art['localizados'] = localizados
    print(f'{nome}: {len(localizados)}/{len(art["quotes"])} trechos localizados')
json.dump(leitura, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if falhas:
    raise SystemExit(f'{falhas} trecho(s) não localizados: corrigir o texto em leitura.json e rodar de novo')
