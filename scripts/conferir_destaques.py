# Gera PNGs das páginas com os destaques desenhados (em memória; o PDF original não é alterado)
# Uso: python conferir_destaques.py leitura_localizada.json pasta_saida [artigo pageIndex ...]
import json, sys, os
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gravar_zotero import cores_por_pergunta

sys.stdout.reconfigure(encoding='utf-8')

leitura = json.load(open(sys.argv[1], encoding='utf-8'))
saida = sys.argv[2]
os.makedirs(saida, exist_ok=True)
cores = {q: tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)) for q, (c, _) in cores_por_pergunta(leitura).items()}
pedidos = sys.argv[3:]
for nome, art in leitura['artigos'].items():
    doc = pymupdf.open(art['pdf'])
    paginas = sorted({a['page'] for a in art['localizados']})
    if pedidos:
        paginas = [int(pedidos[i + 1]) for i in range(0, len(pedidos), 2) if pedidos[i] == nome]
    for pi in paginas:
        page = doc[pi]
        for a in art['localizados']:
            if a['page'] == pi:
                for x0, y0, x1, y1 in a['rects']:
                    # coordenadas Zotero (espaço do PDF) -> espaço da página; retângulo simples
                    # porque o desenho de destaque do PyMuPDF distorce em páginas giradas
                    r = pymupdf.Rect(x0, y0, x1, y1) * page.transformation_matrix
                    page.draw_rect(r, color=None, fill=cores[a['q']], fill_opacity=0.4)
        arq = os.path.join(saida, f'conferir_{nome}_p{pi + 1}.png')
        page.get_pixmap(dpi=80).save(arq)
        print(arq)
