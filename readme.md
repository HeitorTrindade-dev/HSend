<pre style="font-family:'Courier New',Courier,monospace;font-size:12px;line-height:1.17;white-space:pre;background-color:#000;color:#4d8dff;padding:8px;margin:0;">▄▄▄   ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄    ▄▄▄ ▄▄▄▄▄▄
███   ███ █████▀▀▀ ███▀▀▀▀▀ ████▄  ███ ███▀▀██▄
█████████  ▀████▄  ███▄▄    ███▀██▄███ ███  ███
███▀▀▀███    ▀████ ███      ███  ▀████ ███  ███
███   ███ ███████▀ ▀███████ ███    ███ ██████▀</pre>

### Compartilhamento Rápido de Arquivos via Túnel ###

Uma ferramenta de linha de comando que sobe um servidor web local, expõe ele publicamente via **ngrok** e gera um **QR Code** na hora — permitindo enviar textos e arquivos entre dispositivos na mesma rede (ou fora dela) sem precisar instalar nada no dispositivo remetente. Construída em Python com FastAPI.

---

## 🚀 Tech Stack

- **Python 3**
- **FastAPI** para a API e servir os arquivos estáticos
- **Uvicorn** como servidor ASGI
- **pyngrok** para abrir o túnel público automaticamente
- **qrcode** para gerar o QR Code de acesso no terminal
- **HTML / CSS / JS** puro no front-end (`static/index.html`)

---

## 📁 Estrutura do Projeto

```
├── main.py          # Ponto de entrada: sobe o servidor, o túnel e o QR Code
├── configs.py        # Parsing de argumentos da CLI e configuração do ngrok
├── controller.py      # Rotas da API (FastAPI APIRouter)
├── services.py        # Regras de negócio: envio de texto e recebimento de arquivo
├── validacao.py        # Validação da senha global de envio
├── utils.py          # Exibição do QR Code e do banner no terminal
└── static/
    └── index.html      # Interface web usada pelo remetente
```

> Observação: `static/index.html` precisa existir na pasta `static/` na raiz do projeto — é o arquivo servido em `/` e é para onde o FastAPI aponta com `StaticFiles`.

---

## ⚙️ Pré-requisitos

- [Python](https://www.python.org/) 3.8+
- `pip` para instalar as dependências
- Uma conta gratuita no [ngrok](https://dashboard.ngrok.com/get-started/your-authtoken) (o token é pedido automaticamente na primeira execução)

---

## 🛠️ Configuração e Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/HeitorTrindade-dev/HSend
cd Hsend
```

### 2. Instale as dependências

```bash
# Se você tiver um arquivo requirements.txt com o conteúdo fornecido:
pip install -r requirements.txt

# Ou, se preferir instalar via linha de comando:
pip install fastapi uvicorn pyngrok qrcode python-multipart
```

### 3. Instale como comando global

```bash
chmod +x install.sh
sudo bash install.sh
```

Isso cria um symlink em `/usr/local/bin/hdomainhunter`, deixando a ferramenta disponível em qualquer lugar do sistema:
```bash
hsend --help
```

Na primeira execução, o programa vai pedir o token do ngrok — cole o que você pegou no link acima e ele fica salvo para as próximas vezes.

---

## 📡 Uso

```bash
hsend --porta 8000 --senha minhasenha123
```

Isso vai:
1. Abrir um túnel ngrok apontando para a porta escolhida
2. Imprimir o banner e um QR Code no terminal
3. Subir o servidor em `http://127.0.0.1:8000`

Basta escanear o QR Code (ou acessar a URL pública impressa) em qualquer dispositivo para abrir a interface e enviar textos/arquivos.

### 🔧 Argumentos da CLI

| Argumento | Descrição |
|---|---|
| `-p`, `--port`, `--porta` | Porta local do servidor (padrão: `8000`) |
| `-pw`, `-s`, `--password`, `--senha` | Senha exigida para enviar textos/arquivos (opcional — se não for definida, qualquer um pode enviar) |

---

## 🧠 Como Funciona o Fluxo

```
Dispositivo remetente (via QR Code / URL ngrok)
    │
    ▼
[1] Envia texto ou arquivo + senha  →  static/index.html
    │
    ▼
[2] FastAPI recebe a requisição      →  controller.py
    │
    ▼
[3] Valida a senha global            →  validacao.py
    │
    ├── senha incorreta → requisição rejeitada
    │
    ▼ senha correta
[4a] Texto  → impresso no terminal do host
[4b] Arquivo → tamanho/tipo exibidos no terminal
    │
    ▼
[5] Host confirma manualmente no terminal (s/n)
    │
    ├── recusado → arquivo descartado
    │
    ▼ aceito
[6] Arquivo compactado em arquivos_recebidos.zip
    (nomes duplicados recebem sufixo automático)
```

---

## 🧩 Visão Geral dos Módulos

| Módulo | Responsabilidade |
|---|---|
| `main.py` | Ponto de entrada: parseia argumentos, define a senha, sobe o túnel ngrok, mostra banner/QR Code e inicia o Uvicorn |
| `configs.py` | Configura e inicia o ngrok (incluindo captura do token na 1ª vez) e define os argumentos aceitos na CLI |
| `controller.py` | Define as rotas `/`, `/enviar/texto` e `/enviar/arquivo` |
| `services.py` | Lógica de envio de texto e de recebimento/confirmação/compactação de arquivos |
| `validacao.py` | Guarda a senha em variável de ambiente e valida tentativas de envio |
| `utils.py` | Imprime o banner ASCII e renderiza o QR Code no terminal |
| `static/index.html` | Página enviada ao cliente, com formulários de texto e arquivo |

---

## ⚠️ Uso Responsável

Esta ferramenta expõe seu servidor local **publicamente** através do ngrok enquanto estiver rodando. Pontos a ter em mente:

- A senha é **única e global** — não há autenticação por usuário.
- O aceite de arquivos exige confirmação manual no terminal do host, mas a URL pública fica acessível a qualquer pessoa que a receba enquanto o processo estiver ativo.
- Encerre o processo (`Ctrl+C`) assim que terminar de usar, para fechar o túnel e parar de expor a máquina.
- Não use para receber arquivos de fontes não confiáveis sem revisar o conteúdo antes de abrir.
