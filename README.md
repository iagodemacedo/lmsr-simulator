# CPMM Simulator

Um simulador interativo para mercados de previsão usando o mecanismo **Constant Product Market Maker (CPMM)**. Esta aplicação permite simular trades em mercados binários (YES/NO) e analisar os resultados financeiros.

## 🚀 Funcionalidades

### Parâmetros Configuráveis
- **Initial Liquidity (X + Y)**: Liquidez inicial total do pool CPMM
- **Base Fee Rate**: Taxa de fee fixa aplicada em cada trade
- **Initial Probabilities**: Distribuição inicial de probabilidades (YES/NO) que determina X e Y iniciais

### Gerenciamento de Trades
- ✅ Adicionar trades individualmente (Direction: YES/NO e quantidade de Shares)
- ✅ Importar trades em lote via JSON
- ✅ Visualizar todas as trades em tabela interativa
- ✅ Suporte para quantidade ilimitada de trades

### Simulação e Resultados
- Cálculo automático de custos usando fórmula CPMM (X * Y = K)
- Cálculo de fees dinâmicos
- Preço médio por share em cada trade
- Visualização do estado do pool (X, Y, K) antes e depois de cada trade
- Preços atualizados dinamicamente após cada trade
- Resumo financeiro completo:
  - Total Cost Paid
  - Total Fees Earned
  - Final Payout (baseado no resultado do mercado)
  - Net Worth (com cores condicionais: verde para lucro, vermelho para prejuízo)

### Interface
- Interface moderna e intuitiva
- Tabelas com scroll para grandes volumes de dados
- Feedback visual claro para seleções e resultados
- Botões coloridos para seleção de resultado final (YES verde, NO vermelho)
- Visualização do estado inicial e final do pool de liquidez

## 📦 Instalação

### Requisitos
- Python 3.7+
- Streamlit
- NumPy
- Pandas

### Instalação das Dependências

1. **Criar ambiente virtual** (recomendado):
```bash
python3 -m venv venv
```

2. **Ativar o ambiente virtual**:
   - **macOS/Linux**:
   ```bash
   source venv/bin/activate
   ```
   - **Windows**:
   ```bash
   venv\Scripts\activate
   ```

3. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

## 🎯 Como Usar

### Executar a Aplicação

**Opção 1: Usando o script de execução (recomendado para macOS/Linux)**

```bash
./run.sh
```

**Opção 2: Execução manual**

**Importante**: Certifique-se de que o ambiente virtual está ativado antes de executar.

```bash
# Ativar o ambiente virtual (se ainda não estiver ativado)
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Executar a aplicação
streamlit run streamlit_app.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`

### Adicionar Trades Manualmente

1. Configure os parâmetros (Initial Liquidity e Base Fee Rate)
2. Ajuste as probabilidades iniciais usando o slider (opcional)
3. Selecione a direção (YES ou NO) e a quantidade de Shares
4. Clique em "Add Trade" para adicionar à lista

### Importar Trades via JSON

1. Clique em "Modelo JSON" para ver o formato esperado
2. Clique em "Importar JSON"
3. Cole o JSON no campo de texto
4. Clique em "Confirmar Importação"

#### Formato JSON

```json
{
  "trades": [
    {"direction": "YES", "shares": 10},
    {"direction": "NO", "shares": 5},
    {"direction": "YES", "shares": 20}
  ]
}
```

### Executar Simulação

1. Adicione as trades desejadas
2. Selecione o resultado final do mercado (YES ou NO)
3. Visualize os resultados na seção "Simulation Results"

## 📊 Entendendo os Resultados

### Métricas Exibidas

- **X (NO)**: Quantidade de shares NO no pool após cada trade
- **Y (YES)**: Quantidade de shares YES no pool após cada trade
- **K**: Constante de liquidez (X * Y), mantida constante durante todas as trades
- **Price YES**: Preço atual de shares YES (Y / (X + Y))
- **Price NO**: Preço atual de shares NO (X / (X + Y))
- **Cost Paid**: Custo de cada trade calculado pela fórmula CPMM
- **Avg. Price**: Preço médio por share (Cost Paid / Shares)
- **Fee Earned**: Taxa cobrada em cada trade
- **Total Cost Paid**: Soma de todos os custos pagos
- **Total Fees Earned**: Soma de todas as fees cobradas
- **Final Payout**: Quantidade de shares do resultado vencedor possuídas pelo usuário
- **Net Worth**: Lucro líquido (Fees + Payout - Costs Paid)
  - Verde: Lucro positivo
  - Vermelho: Prejuízo

## 🔧 Tecnologias Utilizadas

- **Streamlit**: Framework para aplicações web interativas
- **NumPy**: Cálculos numéricos e matemáticos
- **Pandas**: Manipulação e exibição de dados em tabelas

## 📝 Sobre o CPMM

O **Constant Product Market Maker (CPMM)** é um mecanismo de precificação usado em mercados de previsão e exchanges descentralizadas (como Uniswap). Ele mantém um produto constante entre as reservas de dois ativos, garantindo liquidez sempre disponível.

### Fórmula Base

```
X * Y = K (constante)
```

Onde:
- `X` = quantidade de shares NO no pool
- `Y` = quantidade de shares YES no pool
- `K` = constante de liquidez (produto de X e Y)

### Precificação

Os preços são determinados pela proporção das reservas:

```
Preço YES = Y / (X + Y)
Preço NO = X / (X + Y)
```

### Como Funciona uma Trade

Quando alguém compra shares YES:
- Y aumenta (mais shares YES no pool)
- Para manter K constante, X diminui
- O custo é a diferença em X que precisa ser paga

Quando alguém compra shares NO:
- X aumenta (mais shares NO no pool)
- Para manter K constante, Y diminui
- O custo é a diferença em Y que precisa ser paga

### Características

- **Liquidez Constante**: O produto X * Y sempre permanece constante
- **Preços Dinâmicos**: Os preços mudam automaticamente com base na oferta e demanda
- **Slippage**: Trades maiores causam maior impacto no preço devido à natureza da curva

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👤 Autor

**Iago Macedo**

---

Desenvolvido com ❤️ para simulação de mercados de previsão
