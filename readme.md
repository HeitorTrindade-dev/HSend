<pre style="font-family:'Courier New',Courier,monospace;font-size:12px;line-height:1.17;white-space:pre;background-color:#000;color:#4d8dff;padding:8px;margin:0;">▄▄▄   ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ ▄▄▄    ▄▄▄ ▄▄▄▄▄▄
███   ███ █████▀▀▀ ███▀▀▀▀▀ ████▄  ███ ███▀▀██▄
█████████  ▀████▄  ███▄▄    ███▀██▄███ ███  ███
███▀▀▀███    ▀████ ███      ███  ▀████ ███  ███
███   ███ ███████▀ ▀███████ ███    ███ ██████▀</pre>

### Compartilhamento Rápido e Seguro de Arquivos (Local & Túnel) ###

Uma ferramenta CLI leve e poderosa que sobe um servidor web local com FastAPI, gera um **QR Code** imediato no terminal e opcionalmente expõe via túnel **ngrok** — permitindo enviar textos e arquivos entre celular e computador (e vice-versa) sem precisar instalar nenhum aplicativo no remetente.

---

## 🚀 Tech Stack

- **Python 3.8+**
- **FastAPI** para rotas assíncronas e API REST
- **Uvicorn** como servidor ASGI de alta performance
- **pyngrok** para túneis seguros em redes externas
- **qrcode** para geração de QR Code direto no terminal
- **HTML5 / CSS3 / JavaScript Vanilla** no front-end (`static/index.html`)

---

## 📁 Estrutura do Projeto

```
├── main.py          # Ponto de entrada: orquestra servidor, túnel e inicialização
├── configs.py        # Configurações de CLI, detecção de IP local e túnel ngrok
├── controller.py      # Endpoints da API (FastAPI APIRouter)
├── services.py        # Streaming de arquivos, validação, sanitização e listagem
├── validacao.py        # Autenticação HMAC e proteção contra força bruta (rate limiting)
├── utils.py          # Renderização de QR Code e banner no terminal
├── requirements.txt   # Dependências do projeto
├── install.sh         # Script de instalação global do comando 'hsend'
└── static/
    └── index.html     # Interface web moderna com drag-and-drop e progresso
```

---

## ⚙️ Pré-requisitos

- [Python](https://www.python.org/) 3.8+
- `pip` para instalar as dependências
- *(Opcional)* Uma conta no [ngrok](https://dashboard.ngrok.com/get-started/your-authtoken) se desejar acesso fora da mesma rede Wi-Fi.

---

## 🛠️ Configuração e Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/HeitorTrindade-dev/HSend.git
cd HSend
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Instale como comando global (Opcional)

```bash
chmod +x install.sh
sudo bash install.sh
```

Isso cria o comando `hsend` em `/usr/local/bin/hsend`, permitindo executá-lo a partir de qualquer pasta:
```bash
hsend --help
```

---

## 📡 Uso

### Modo Rápido (Rede Local / Wi-Fi)
Para transferências muito mais rápidas entre aparelhos no mesmo Wi-Fi, sem depender de internet nem de conta no ngrok:
```bash
hsend --no-tunnel
```

### Modo Túnel Público (ngrok)
Expõe o servidor publicamente para transferências pela internet:
```bash
hsend
```

### Com Senha e Pasta Customizada
```bash
hsend --senha minhasenha123 --output ~/Downloads/recebidos -y
```

### 🔧 Argumentos da CLI

| Argumento | Descrição |
|---|---|
| `-p`, `--port`, `--porta` | Porta local do servidor (padrão: `8000`) |
| `-pw`, `-s`, `--password`, `--senha` | Senha exigida para envio e download (opcional) |
| `-o`, `--output`, `--output-dir` | Diretório onde os arquivos serão salvos (padrão: `./recebidos`) |
| `-y`, `--yes`, `--auto-accept` | Aceita arquivos automaticamente sem confirmação interativa no terminal |
| `--no-tunnel`, `--local` | Executa somente na rede local (Wi-Fi), sem abrir túnel ngrok |
| `--zip` | Salva arquivos recebidos compactados em um arquivo `.zip` |

---

## ✨ Principais Recursos e Melhorias

- **⚡ Streaming em Chunks**: Arquivos grandes de até 500 MB são gravados em disco via streaming (1 MB por chunk), sem risco de estouro de memória RAM.
- **🔒 Segurança & Rate Limiting**: Comparação de senha em tempo constante (`hmac.compare_digest`) e bloqueio automático de IP após 5 tentativas incorretas.
- **🛡️ Prevenção contra Path Traversal**: Nomes de arquivo são rigorosamente sanitizados, impedindo ataques de travessia de diretório ou Zip Slip em Linux e Windows.
- **🔄 Transferência Bidirecional**: Além de enviar arquivos para o computador, a interface web permite listar e baixar de volta no celular os arquivos salvos.
- **📊 Progresso de Upload em Tempo Real**: Feedback visual com barra de progresso percentual via `XMLHttpRequest.upload`.
- **📁 Múltiplos Arquivos e Drag-and-Drop**: Permite arrastar e soltar múltiplos arquivos simultaneamente.
- **🤝 Concorrência Segura**: Lock assíncrono para o prompt no terminal, com timeout automático de 60 segundos caso o operador esteja ausente.
- **🧹 Encerramento Limpo**: Limpeza automática de processos e túneis do ngrok ao fechar o terminal (`Ctrl+C`).
