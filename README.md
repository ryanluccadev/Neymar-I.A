# Neymar IA

Assistente virtual para Windows desenvolvido em Python, com interface gráfica, interação por voz e texto, integração com modelos de IA e automações do sistema.

## Principais funcionalidades

- Interação por voz e texto.
- Ativação por voz e processamento de comandos.
- Interface gráfica com ícone e bandeja do sistema.
- Integração com Gemini, Groq e Cohere.
- Pesquisa na internet com Tavily.
- Histórico de conversas em SQLite.
- Memória persistente em SQLite.
- Controle de músicas e Deezer.
- Pesquisa e abertura de conteúdo no YouTube.
- Automação do Windows, programas e janelas.
- Comandos relacionados a mídia, streaming e FC 26.
- Inicialização opcional com o Windows.

## Estrutura

```text
Neymar-I.A/
├── Neymar_IA.py
├── Neymar IA.spec
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── neymar_ia/
    ├── __init__.py
    ├── audio.py
    ├── clients.py
    ├── comandos.py
    ├── config.py
    ├── fc26.py
    ├── historico.py
    ├── ia.py
    ├── inicializacao.py
    ├── interface.py
    ├── memoria.py
    ├── midia.py
    ├── modos.py
    ├── musica.py
    ├── pesquisa.py
    ├── sistema.py
    ├── streamings.py
    ├── youtube.py
    └── assets/
        ├── neymar_ia.ico
        └── neymar_ia.png
```

O arquivo principal é **`Neymar_IA.py`**.

Existe somente um arquivo de configuração do PyInstaller: **`Neymar IA.spec`**.

## Instalação

No Windows, abra o PowerShell na pasta do projeto:

```powershell
cd "CAMINHO\DO\PROJETO"

python -m venv venv

.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

pip install pyinstaller
```

Se o PowerShell bloquear a ativação, execute o comando de acordo com a política de execução configurada no seu Windows.

## Configuração das APIs

Copie `.env.example` para `.env` e preencha apenas as chaves que você possui:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
COHERE_API_KEY=
TAVILY_API_KEY=
```

O `.env` não deve ser enviado ao Git ou compartilhado publicamente.

As chaves são carregadas automaticamente na inicialização por `python-dotenv`.

Também é possível configurar opcionalmente:

- `NEYMAR_MICROFONE`: parte do nome do microfone preferido.
- `NEYMAR_CAMINHO_FC26`: caminho do executável do FC 26.

## Executar pelo Python

Com a virtualenv ativada:

```powershell
python Neymar_IA.py
```

## Criar o executável

Depois de instalar o PyInstaller:

```powershell
python -m PyInstaller --clean "Neymar IA.spec"
```

O executável será gerado em:

```text
dist\Neymar IA.exe
```

A configuração usa:

- `Neymar_IA.py` como ponto de entrada.
- Todos os submódulos de `neymar_ia` como hidden imports.
- `neymar_ia/assets` no executável.
- `neymar_ia/assets/neymar_ia.ico` como ícone.
- `console=False`, evitando a abertura de um terminal junto da interface.

## Recompilar após alterar o código

Não é necessário instalar todas as dependências novamente. Com a virtualenv ativada, execute:

```powershell
.\venv\Scripts\Activate.ps1

python -m PyInstaller --clean "Neymar IA.spec"
```

Isso gera novamente:

```text
dist\Neymar IA.exe
```

com as alterações atuais.

## Dados persistentes

Os bancos de memória e histórico são gravados em uma pasta de dados gravável do usuário, fora do executável. No Windows, normalmente ficam dentro de `LOCALAPPDATA\Neymar IA\data` (ou `APPDATA` quando necessário).

Assim, memória e histórico não dependem da pasta temporária usada pelo PyInstaller e continuam disponíveis entre execuções do `.exe`.

## Observações

- `build/`, `dist/`, virtualenvs, caches e bancos locais são ignorados pelo `.gitignore`.
- Não há `main.py` no projeto.
- Não há um segundo arquivo `.spec`.
- O PyInstaller é uma ferramenta de build e, por isso, é instalado separadamente de `requirements.txt`.
