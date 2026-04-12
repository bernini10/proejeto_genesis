# 👑 PROJECT GÊNESIS: DETERMINISTIC KINETIC ENGINE (V6-TITÃ)

![Status](https://img.shields.io/badge/Status-Validated-brightgreen)
![Version](https://img.shields.io/badge/Version-6.0.0--Tita-gold)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Market](https://img.shields.io/badge/Market-Crypto-blue)

## 🌌 1. O MANIFESTO: A LEI DETERMINÍSTICA DE SEVERINO

O **Projeto Gênesis** não é um robô de indicadores. É um **Motor de Execução Cinética**. O fundamento central deste projeto é a negação da aleatoriedade do mercado em janelas de transição de fase. 

Através da **Lei de Severino**, provamos que o preço, quando submetido a vetores de aceleração específicos após romper barreiras de volatilidade comprimida (0.5 Sigma), entra em um estado de fluxo determinístico. O sistema não "adivinha" o futuro; ele reage a leis físicas de inércia e exaustão térmica.

---

## 🔬 2. ARQUITETURA TÉCNICA DETALHADA (CORE)

### 🚀 A. Pipeline de Física Teórica (`core/physics.py`)
A inteligência reside na transformação da série temporal em dados vetoriais:
* **Cálculo de Velocity ($v$):** Derivada de primeira ordem do preço em relação ao tempo, normalizada para eliminar o ruído escalar.
* **Cálculo de Acceleration ($a$):** Derivada de segunda ordem ($dv/dt$). Atua como o validador de inércia. Se $a \leq 0$ no rompimento, o sinal é descartado como "falso vácuo".
* **Compressão Sigma:** Diferente do padrão de mercado (2.0 Sigma), utilizamos **0.5 Sigma** sobre a Média Móvel Simples (SMA-20). Isso nos permite capturar a ignição do movimento, não o seu clímax.

### ⚙️ B. O Motor de Combustão Dual (Long & Short)
O sistema opera em simetria total. O lucro é extraído tanto da propulsão (Long) quanto da gravidade (Short):
* **Long:** $Price > UpperWall \text{ AND } v > threshold \text{ AND } a > 0$
* **Short:** $Price < LowerWall \text{ AND } v < -threshold \text{ AND } a < 0$
* **Exit Strategy:** Saída obrigatória no toque da média móvel (Equilíbrio Térmico), garantindo o lucro antes da reversão da entropia.

---

## 📈 3. RESULTADOS DE BACKTEST E VALIDAÇÃO DE ESTRESSE

O sistema foi submetido a um **Colisor de Timeframes**, testando todas as combinações binárias possíveis. O par **30m (Âncora) / 5m (Execução)** emergiu como o Ponto Crítico Ótimo.

| Métrica | Bitcoin (BTC) | Ethereum (ETH) |
| :--- | :--- | :--- |
| **Retorno Acumulado** | **+8.586,42%** | **+4.623.880,32%** |
| **Profit Factor** | 2.88 | 2.83 |
| **Win Rate** | 62.58% | 56.41% |
| **Lucro Mensal Médio** | **6.11%** | **15.33%** |
| **Sortino Ratio** | 4.71 | 6.73 |
| **Expectancy** | 9.31 | 1796.37 |

### 🌪️ Teste de Resistência ao Atrito (Slippage Test)
O sistema foi validado simulando **0.2% de taxas/slippage** por trade. Mesmo sob estresse extremo, o sistema manteve retornos superiores a 1000% no período, provando robustez matemática contra a latência de execução.

---

## 📂 4. ESTRUTURA DO REPOSITÓRIO

* `core/`: Bibliotecas de física e processamento de vetores.
* `genesis_tita_final/`: Santuário do motor BTC (Sensibilidade 0.5).
* `genesis_tita_eth/`: Santuário do motor ETH (Sensibilidade 0.02).
* `data/`: Repositório de dados históricos (Parquet).
* `tests/`: Scripts de validação e auditoria contábil.
* `estrategias_validadas/`: Histórico de evolução das versões v1 a v6.

---

## 🤝 5. COLABORAÇÃO E CONTRIBUIÇÃO

Este é um projeto de **Código Proprietário e Privado**. Colaboradores devem seguir o **Protocolo Severino**:
1.  **Lógica Primeiro:** Nenhuma alteração de código é permitida sem uma prova matemática de aumento no Profit Factor.
2.  **Surgical Changes:** Edições mínimas, mantendo a integridade do pipeline original.
3.  **Audit Trail:** Todo novo teste deve ser registrado com um script de auditoria contábil.

---

## 🛡️ 6. LICENÇA E AVISO LEGAL

**Propriedade Intelectual:** Mestre Bernini / Severino-AI.
**Licença:** Todos os direitos reservados. O uso deste código para operações reais envolve risco financeiro. A Lei Determinística é uma ferramenta estatística de alta probabilidade, não uma garantia de lucro futuro.

---
**"No mercado, como na física, a força sem aceleração é apenas peso morto."**
