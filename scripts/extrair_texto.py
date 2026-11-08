# Extrai o texto de um PDF com marcadores de página (índice do PDF e número impresso)
# Uso: python extrair_texto.py arquivo.pdf saida.txt
import sys
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open(sys.argv[1])
with open(sys.argv[2], 'w', encoding='utf-8') as out:
    for i, p in enumerate(doc):
        out.write(f"\n===== pageIndex {i} | PDF p. {i + 1} | rótulo {p.get_label()!r} =====\n")
        out.write(p.get_text())
print(f'{len(doc)} páginas; rótulos impressos: {"sim" if doc[0].get_label() else "não"}')
