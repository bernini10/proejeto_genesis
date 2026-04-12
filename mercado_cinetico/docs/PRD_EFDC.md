# PRD - Engenharia de Fractais e Dinâmica do Caos (EFDC)
# Objetivo: Identificar regimes de Ordem vs Caos

## Componentes Técnicos:
1. **Exponente de Hurst (H):** - H > 0.5 (Persistência)
   - H < 0.5 (Anti-persistência/Ruído)
2. **Dimensão Fractal (D):** Medição da rugosidade do gráfico via Algoritmo de Sevcik.
3. **Mudança de Fase:** Detecção de transição de Entropia.

## Regras de Entrada:
- Operar apenas quando H > 0.65 (Tendência com memória fractal).
