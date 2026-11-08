# Lista os artigos de uma coleção do Zotero (API local, só leitura) com chaves, PDF e notas já existentes
# Uso: python listar_colecao.py "Nome da coleção"
import json, sys, urllib.request, urllib.parse

BASE = 'http://localhost:23119/api/users/0'


def get(path):
    with urllib.request.urlopen(BASE + path) as r:
        return r.read().decode('utf-8')


sys.stdout.reconfigure(encoding='utf-8')
nome = sys.argv[1]
# A API local não lista anotações em /children: contar pela busca global
n_anot, start = {}, 0
while True:
    lote = json.loads(get(f'/items?itemType=annotation&limit=100&start={start}'))
    for a in lote:
        n_anot[a['data']['parentItem']] = n_anot.get(a['data']['parentItem'], 0) + 1
    if len(lote) < 100:
        break
    start += 100
cols = json.loads(get('/collections?limit=500'))
achadas = [c for c in cols if c['data']['name'].lower() == nome.lower()]
if not achadas:
    raise SystemExit(f'Coleção "{nome}" não encontrada. Nomes parecidos: '
                     + ', '.join(c['data']['name'] for c in cols if nome.lower()[:4] in c['data']['name'].lower()))
for col in achadas:
    print(f"COLEÇÃO {col['data']['name']} key={col['key']} itens={col['meta'].get('numItems')}")
    itens = json.loads(get(f"/collections/{col['key']}/items/top?limit=100"))
    for it in itens:
        d = it['data']
        autores = '; '.join(c.get('lastName') or c.get('name', '') for c in d.get('creators', []))
        print(f"\nITEM {it['key']} | {d['itemType']} | {d.get('date', '')} | DOI {d.get('DOI', '')}")
        print(f"  título: {d.get('title', '')}")
        print(f"  autores: {autores}")
        print(f"  revista: {d.get('publicationTitle', '')} v.{d.get('volume', '')} n.{d.get('issue', '')} p.{d.get('pages', '')}")
        for ch in json.loads(get(f"/items/{it['key']}/children")):
            cd = ch['data']
            if cd['itemType'] == 'attachment' and cd.get('contentType') == 'application/pdf':
                url = get(f"/items/{ch['key']}/file/view/url").strip()
                caminho = urllib.request.url2pathname(urllib.parse.urlparse(url).path)
                print(f"  PDF {ch['key']} | {caminho} | {n_anot.get(ch['key'], 0)} anotações já existentes")
            elif cd['itemType'] == 'note':
                tags = [t['tag'] for t in cd.get('tags', [])]
                print(f"  NOTA {ch['key']} | tags {tags} | {cd['note'][:80]!r}")
