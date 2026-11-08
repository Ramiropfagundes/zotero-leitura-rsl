---
name: zotero-leitura-rsl
description: Lê os artigos (PDF) de uma coleção do Zotero, responde perguntas de leitura com base no texto e grava no próprio Zotero uma nota de leitura por artigo (respostas, trechos citados, páginas e links rastreáveis) e destaques coloridos no PDF, uma cor por pergunta. Use quando o usuário pedir para ler/fichar/extrair dados dos artigos de uma coleção do Zotero, responder perguntas de RSL sobre eles, ou marcar os PDFs no Zotero.
---

# Leitura de coleção do Zotero com notas e destaques

Instalação e configuração: ver `README.md` nesta pasta.

## Antes de começar

1. Confirmar com o usuário: **nome da coleção** e **perguntas**. Se ele não der perguntas, oferecer as 4 perguntas sugeridas (abaixo) e esperar a confirmação.
2. O Zotero Desktop precisa estar aberto, com a API local ativada (Configurações → Avançado → "Permitir que outros aplicativos neste computador se comuniquem com o Zotero"). Ela responde em `localhost:23119` e é só leitura.
3. A gravação usa a API web do Zotero e precisa de duas variáveis de ambiente do usuário: `ZOTERO_USER_ID` (número) e `ZOTERO_API_KEY` (chave com permissão de escrita). O script lê as duas sozinho; **nunca exibir a chave**. Se faltar alguma, o script avisa: orientar o usuário com o `README.md`.
4. Conferir se o Python tem o PyMuPDF: `python -c "import pymupdf"` (no Mac/Linux pode ser `python3`). Se faltar, pedir ao usuário autorização para rodar `pip install pymupdf`.
5. Trabalhar no scratchpad da sessão (ou numa pasta temporária). Os scripts ficam em `~/.claude/skills/zotero-leitura-rsl/scripts/` (abaixo: `$SK`).

### Perguntas sugeridas para RSL

- Q1: Qual é o tipo de problema que o artigo está tratando?
- Q2: Como esse problema foi endereçado (métodos e metodologia utilizada)?
- Q3: Por qual motivo essa metodologia foi utilizada para este problema especificamente?
- Q4: Quais são as limitações da metodologia utilizada e as limitações do estudo em geral? (apontam lacunas científicas)

As cores seguem a ordem das perguntas: amarelo, verde, azul, vermelho, roxo, magenta, laranja e cinza.

## Passos

1. **Listar a coleção:** `python $SK/listar_colecao.py "Nome"`. Mostra as chaves do item e do PDF, o caminho do arquivo, os metadados e as notas que já existem. Se já houver nota com a tag `nota-leitura-claude`, perguntar se é para refazer. Itens sem PDF: avisar e pular.
2. **Extrair o texto:** `python $SK/extrair_texto.py arquivo.pdf saida.txt`. Ler o texto **inteiro** de cada artigo, em partes se for longo. Referências e anexos podem ser lidos só por cima, a não ser que tragam conteúdo metodológico. Se o PDF não tiver texto (escaneado), avisar o usuário: precisa de OCR.
3. **Montar o `leitura.json`** na pasta de trabalho (formato abaixo, exemplo em `exemplo_leitura.json`). Regras de conteúdo:
   - Responder **só com base no texto**. Se não houver resposta, escrever explicitamente "**não encontrado no texto**" e dizer o que falta. Nunca inventar.
   - Separar o que os autores dizem do que é inferência. A inferência vai num parágrafo marcado "**Observação do leitor (Claude, não está no texto):**". Isso vale principalmente para Q3 (justificativa implícita) e Q4 (limitações não declaradas, que apontam lacunas).
   - Cada resposta cita as páginas impressas, por exemplo "(p. 553)".
   - Trechos (`quotes`): copiar **literalmente** do texto extraído, sem o hífen de quebra de linha. Usar de 1 a 5 trechos por pergunta. Um trecho não pode atravessar páginas: quebrar em dois. O trecho precisa ser único na página.
   - Escrever as respostas no idioma do usuário. Os trechos ficam no idioma original.
4. **Localizar:** `python $SK/localizar_trechos.py leitura.json leitura_localizada.json`. Se algum trecho falhar, corrigir o texto e rodar de novo.
5. **Conferir visualmente:** `python $SK/conferir_destaques.py leitura_localizada.json pasta [artigo pageIndex ...]`. Abrir 1 ou 2 PNGs com Read e checar se os grifos cobrem os trechos certos.
6. **Gravar:** `python $SK/gravar_zotero.py leitura_localizada.json registro.json`. Cria os destaques e uma nota filha por artigo, e pula artigos que já tenham nota com o mesmo ID (`--forcar` grava de novo). O PDF original **não é alterado**: os destaques são anotações do Zotero.
7. **Avisar o usuário** para sincronizar o Zotero (setas verdes) e conferir. Relatar quantos destaques e notas foram criados por artigo e listar as perguntas sem resposta no texto.

## Formato do `leitura.json`

```json
{
 "colecao": "Minha_RSL", "colecao_key": "ABCD1234", "data": "AAAA-MM-DD",
 "perguntas": {"Q1": "texto da pergunta", "Q2": "..."},
 "artigos": {
  "apelido": {
   "id": "Autor2024",            // vira o ID da nota: RSL-<colecao>-<id>
   "item": "ITEMKEY1",           // chave do item pai
   "attachment": "PDFKEY01",     // chave do anexo PDF
   "pdf": "caminho/do/arquivo.pdf",   // como aparece na saída do listar_colecao.py
   "first_page": 95,             // página impressa da 1ª página do PDF (usada só se o PDF não tiver rótulos)
   "cite": "Autor (2024)", "doi": "10.xxxx/...",
   "reference": "Referência completa (ABNT)",
   "answers": {"Q1": ["parágrafo (HTML simples permitido: <b>, <i>)", "..."], "Q2": ["..."]},
   "quotes": [["Q1", 0, "trecho literal na página de pageIndex 0"], ["Q2", 3, "..."]]
  }
 }
}
```

`pageIndex` começa em 0 e é o número que aparece nos marcadores `===== pageIndex N` do texto extraído.

## O que a nota contém (rastreabilidade)

- Título "RSL <coleção> – Leitura: <citação>".
- Referência completa, DOI, chaves do item e do PDF, coleção e o ID único `RSL-<coleção>-<id>`, com a data.
- Para cada pergunta: a resposta, seguida da lista de evidências. Cada evidência traz o trecho entre aspas, a página impressa e a página do PDF, e um link `zotero://open-pdf` que abre o destaque.
- Tags: `RSL-<coleção>` e `nota-leitura-claude` na nota; `RSL-Qn`, `RSL-<coleção>` e `claude` nos destaques.

## Observações técnicas

- Só funciona com a **biblioteca pessoal** (Minha Biblioteca), não com bibliotecas de grupo.
- As coordenadas do Zotero seguem o padrão do PDF sem rotação (origem no canto inferior esquerdo). O script faz a conversão e para se a página tiver cropbox deslocada.
- Páginas giradas (tabelas em paisagem): o script localiza normalmente e emite um AVISO. Nesses casos, pedir ao usuário que confira esse destaque no Zotero.
- A API local não lista anotações em `/items/<pdf>/children`. Para contá-las, usar `items?itemType=annotation`, como faz o `listar_colecao.py`.
- Os destaques e as notas sincronizam como metadados: funcionam mesmo que a sincronização de arquivos esteja desligada.
- Coleções grandes: processar em lotes de 3 a 5 artigos e mostrar o primeiro lote ao usuário antes de seguir.
