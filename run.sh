#!/bin/bash

# Script para executar o simulador CPMM
# Verifica se o ambiente virtual existe, cria se necessário, e executa o app

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Verificando dependências..."
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

echo "Iniciando simulador CPMM..."
streamlit run streamlit_app.py

