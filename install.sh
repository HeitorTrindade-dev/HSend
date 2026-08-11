#!/bin/bash

VERDE="\033[32m"
VERMELHO="\033[31m"
RESET="\033[0m"

if [ "$EUID" -ne 0 ]; then
  echo -e "${VERMELHO}[-] Por favor, execute este script com sudo:${RESET}"
  echo "sudo bash install.sh"
  exit 1
fi

DIRETORIO_ATUAL=$(pwd)
ARQUIVO_PRINCIPAL="$DIRETORIO_ATUAL/main.py"
NOME_COMANDO="hsend"
DESTINO="/usr/local/bin/$NOME_COMANDO"

# Verifica se o main.py existe na pasta
if [ ! -f "$ARQUIVO_PRINCIPAL" ]; then
  echo -e "${VERMELHO}[-] Erro: 'main.py' não foi encontrado nesta pasta!${RESET}"
  exit 1
fi

echo "[+] Instalando o HSend..."

chmod +x "$ARQUIVO_PRINCIPAL"

if [ -L "$DESTINO" ] || [ -f "$DESTINO" ]; then
  rm -f "$DESTINO"
fi
ln -s "$ARQUIVO_PRINCIPAL" "$DESTINO"

echo -e "${VERDE}[+] Sucesso! O comando '$NOME_COMANDO' foi instalado globalmente.${RESET}"
echo -e "${VERDE}[+] Agora você pode rodar de qualquer lugar digitando: ${RESET}hsend --help"
