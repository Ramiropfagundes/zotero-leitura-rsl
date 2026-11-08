# Skill zotero-leitura-rsl: instalação

Esta skill faz o Claude Code ler os PDFs de uma coleção do Zotero, responder às suas perguntas de leitura (por exemplo, as de uma revisão sistemática) e gravar no seu Zotero:

- uma **nota de leitura** por artigo, com as respostas, os trechos citados e as páginas;
- **destaques coloridos** no PDF, uma cor por pergunta.

O PDF original não é alterado: os destaques são anotações do Zotero.

## Do que você precisa

- **Claude Code** instalado (terminal, VS Code ou app desktop).
- **Zotero 7** (desktop), com conta em zotero.org e a sincronização ligada.
- **Python 3** com a biblioteca **PyMuPDF**.

## Passo 1: copiar a pasta da skill

**Opção A, com git** (facilita receber atualizações depois com `git pull` dentro da pasta):

```
git clone https://github.com/Ramiropfagundes/zotero-leitura-rsl.git ~/.claude/skills/zotero-leitura-rsl
```

**Opção B, sem git:** no GitHub, clique em **Code → Download ZIP**, descompacte e renomeie a pasta para `zotero-leitura-rsl` (o GitHub acrescenta `-main` ao nome).

Nos dois casos, a pasta precisa ficar assim:

- **Windows:** `C:\Users\<seu-usuário>\.claude\skills\zotero-leitura-rsl\SKILL.md`
- **Mac/Linux:** `~/.claude/skills/zotero-leitura-rsl/SKILL.md`

Se a pasta `skills` não existir, crie. A pasta `.claude` fica oculta: no Windows, digite o caminho na barra do Explorador; no Mac, use Cmd+Shift+. no Finder.

## Passo 2: instalar o PyMuPDF

No terminal:

```
pip install pymupdf
```

(no Mac/Linux pode ser `pip3 install pymupdf`)

## Passo 3: ativar a API local do Zotero

No Zotero: **Editar → Configurações → Avançado** (no Mac: Zotero → Configurações → Avançado) e marque **"Permitir que outros aplicativos neste computador se comuniquem com o Zotero"**.

## Passo 4: criar a chave da API e pegar seu userID

1. Entre em <https://www.zotero.org/settings/keys> (logado na sua conta).
2. No topo da página aparece **"Your user ID for use in API calls is NNNNNNN"**: anote esse número.
3. Clique em **Create new private key**, dê um nome (ex.: "Claude"), marque **Allow library access** e **Allow write access**, e salve.
4. Copie a chave gerada. **Não compartilhe essa chave com ninguém**: ela dá acesso de escrita à sua biblioteca.

## Passo 5: salvar as duas variáveis de ambiente

**Windows** (PowerShell, troque os valores):

```
[Environment]::SetEnvironmentVariable('ZOTERO_USER_ID', 'SEU_NUMERO', 'User')
[Environment]::SetEnvironmentVariable('ZOTERO_API_KEY', 'SUA_CHAVE', 'User')
```

**Mac** (zsh) ou **Linux** (troque `.zshrc` por `.bashrc` se usar bash):

```
echo 'export ZOTERO_USER_ID="SEU_NUMERO"' >> ~/.zshrc
echo 'export ZOTERO_API_KEY="SUA_CHAVE"' >> ~/.zshrc
```

Depois **feche e abra de novo** o terminal / VS Code / Claude Code.

## Como usar

Com o Zotero aberto, peça ao Claude Code algo como:

> Leia os artigos da coleção "Minha_RSL" do Zotero e responda às perguntas da RSL.

O Claude confirma a coleção e as perguntas, lê os artigos, mostra o resultado e grava no Zotero. Ao final, clique nas setas verdes de sincronização do Zotero e confira as notas e os destaques.

## Limitações

- Só a **biblioteca pessoal** (Minha Biblioteca); bibliotecas de grupo não funcionam.
- PDFs escaneados (sem texto) precisam de OCR antes.
- As respostas são geradas pelo Claude a partir do texto: confira sempre antes de usar na sua pesquisa. A nota separa o que está no artigo do que é inferência do leitor.
