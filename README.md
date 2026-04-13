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


Para entender, pense no bot como um radar de trânsito observando um carro em uma subida:

1. Velocidade 30m (+0.006) = A Direção Atual
A velocidade positiva significa que, no balanço dos últimos 30 minutos, o preço está mais alto do que estava antes. O "carro" está se movendo para cima (tendência de alta).

2. Aceleração 5m (-0.007) = A Perda de Força
A aceleração negativa significa que a velocidade está diminuindo.

Imagine que o preço subiu 1% na janela anterior, mas nesta janela de 5 minutos ele subiu apenas 0.2%.

O movimento ainda é para cima (Velocidade +), mas ele está "freiando" ou perdendo o fôlego (Aceleração -).

Como isso funciona na prática (Física do Mercado)
A relação entre os dois indica o Ciclo de Vida do movimento:
Velocidade,Aceleração,O que significa?,Decisão do Bot V6
Positiva (+),Positiva (+),Subindo e ganhando força (Explosão).,IGNIÇÃO BUY (Compra)
Positiva (+),Negativa (-),"Subindo, mas perdendo força (Exaustão).",AGUARDANDO (Risco de topo)
Negativa (-),Negativa (-),Caindo e ganhando força na queda.,IGNIÇÃO SHORT (Venda)
Negativa (-),Positiva (+),"Caindo, mas freiando a queda.",AGUARDANDO (Risco de fundo)



Aqui está o processo passo a passo:

### 1. A Matéria-Prima (DataFrame)
O bot baixa os últimos 60 candles (velas) da Bitget. Cada vela contém o preço de fechamento (`close`).

### 2. O Cálculo da Velocidade ($v$)
Diferente de um velocímetro de carro que mede distância por tempo, no trading a "distância" é a variação do preço. No seu código, a velocidade é a **Variação Percentual (Percent Change)**.

A fórmula aplicada no `physics.py` é:
$$v = \frac{Preço_{atual} - Preço_{anterior}}{Preço_{anterior}}$$

* **Na prática:** Se o BTC estava em $70.000 e foi para $70.700, a velocidade é de **+0.01** (ou 1%).
* **O que o bot vê:** Se esse valor for maior que o seu **Sigma** (ex: 0.005), ele entende que o mercado tem "pressa" para subir.

### 3. O Cálculo da Aceleração ($a$)
A aceleração mede a **mudança na velocidade**. Ela serve para saber se o mercado está ganhando tração ou se está "cansando".

A fórmula aplicada é a diferença entre a velocidade da vela atual e a velocidade da vela anterior:
$$a = v_{atual} - v_{anterior}$$

* **Exemplo de Aceleração Positiva:**
    * Vela 1: Velocidade +0.001
    * Vela 2: Velocidade +0.005
    * **Aceleração:** $0.005 - 0.001 = +0.004$ (O preço está subindo cada vez mais rápido).

* **Exemplo de Aceleração Negativa (o que você viu no seu print):**
    * Vela 1: Velocidade +0.006
    * Vela 2: Velocidade +0.002
    * **Aceleração:** $0.002 - 0.006 = -0.004$ (O preço ainda está subindo, mas a força da subida diminuiu drasticamente).

---

### 4. A Tomada de Decisão (A Lógica V6)

O bot não olha apenas para esses números isolados. Ele os cruza para garantir a **Simetria Total** que você testou no backtest:

1.  **Filtro de Tendência:** O preço atual deve estar acima da Média de 30m + 0.5 Desvios (garante que não é apenas um "ruído" lateral).
2.  **Confirmação de Direção:** A Velocidade 30m deve ser maior que o Sigma (garante que há volume direcional).
3.  **Confirmação de Explosão:** A Aceleração 5m **precisa ser positiva** (garante que você está entrando no início de um impulso, e não no final dele).



### Por que usar 30m para Velocidade e 5m para Aceleração?
* **Velocidade (30m):** Serve como uma **âncora**. Ela te diz para onde o "navio" maior está indo.
* **Aceleração (5m):** Serve como o **gatilho**. Ela observa as pequenas oscilações rápidas para decidir o segundo exato de "apertar o botão", evitando que o bot entre atrasado na operação.

Se a aceleração está negativa, como no seu print, o bot interpreta que o "combustível" daquela subida acabou momentaneamente, por isso ele mantém o status em **AGUARDANDO**.

---
**"No mercado, como na física, a força sem aceleração é apenas peso morto."**
