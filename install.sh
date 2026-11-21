#!/bin/bash

VERDE="\033[32m"
VERMELHO="\033[31m"
RESET="\033[0m"

if [ "$EUID" -ne 0 ]; then
  echo -e "${VERMELHO}[-] Por favor, execute este script com sudo:${RESET}"
  echo "sudo bash install.sh"
  exit 1
fi

DIRETORIO_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARQUIVO_PRINCIPAL="$DIRETORIO_SCRIPT/main.py"
NOME_COMANDO="hsend"
DESTINO="/usr/local/bin/$NOME_COMANDO"

if [ ! -f "$ARQUIVO_PRINCIPAL" ]; then
  echo -e "${VERMELHO}[-] Erro: 'main.py' não foi encontrado em $DIRETORIO_SCRIPT!${RESET}"
  exit 1
fi

echo "[+] Instalando o HSend globalmente..."

chmod +x "$ARQUIVO_PRINCIPAL"

# Cria um wrapper executável em /usr/local/bin
cat << EOF > "$DESTINO"
#!/bin/bash
exec python3 "$ARQUIVO_PRINCIPAL" "\$@"
EOF

chmod +x "$DESTINO"

echo -e "${VERDE}[+] Sucesso! O comando '$NOME_COMANDO' foi instalado globalmente em $DESTINO.${RESET}"
echo -e "${VERDE}[+] Agora você pode rodar de qualquer diretório digitando: ${RESET}hsend --help"
