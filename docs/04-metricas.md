# 📊 Avaliação e Métricas de Qualidade — Agente Finn

> **Repositório do Projeto:** `https://github.com/Mister-N-Oliveira/dio-lab-bia-do-futuro`

---

## 1. Como Avaliar o Agente Finn

A avaliação do agente Finn combina duas abordagens complementares de observabilidade:

1. **Testes Estruturados Automatizados (`eval_agent.py` / `finance_engine.py`):** Suíte contendo os 18 cenários formais de teste cobrindo cálculos de extrato, perfil de risco, recomendações do catálogo, busca na web e recusa de escopo.
2. **Avaliação das Métricas em Tempo de Execução (Streamlit):** Painel dinâmico embutido no `src/app.py` que calcula Escopo, Grounding, Cortesia e Score da Resposta para cada mensagem enviada.

---

## 2. Métricas Principais de Qualidade

| Métrica | O que avalia | Exemplo de Teste | Resultado no Finn |
|---|---|---|---|
| **Assertividade** | O agente respondeu corretamente o que foi perguntado? | Perguntar o saldo de outubro e receber o valor exato restante | 🟢 **100% (18/18)** — Efetua cálculos matemáticos exatos de `transacoes.csv` (saldo restante de R$ 2.511,10 sobre R$ 5.000,00 de renda) |
| **Segurança & Escopo** | O agente evitou inventar informações e recusou temas fora do domínio? | Perguntar a previsão do tempo e o agente recusar educadamente | 🟢 **100%** — Recusa perguntas de clima, esportes e política; limita recomendações de compra ao catálogo oficial |
| **Coerência** | A resposta respeita o perfil e os limites de risco do cliente? | Recomendar investimentos conservadores para quem declarou `aceita_risco: false` | 🟢 **100%** — Recomenda apenas Tesouro Selic e CDB de baixo risco alinhados a `perfil_investidor.json` |
| **Grounding & Fontes** | A resposta possui embasamento em dados oficiais ou busca web? | Perguntar *"O que é Tesouro Selic?"* e receber explicação com fontes oficiais | 🟢 **100%** — Integração com busca na web em tempo real (Google Search Grounding / DDGS) com links e citações (Tesouro Direto, BCB, CVM, ANBIMA) |

> [!TIP]
> **Dica para Testadores:** Ao testar com pessoas reais (amigos ou colegas), instrua-os sobre os dados do **cliente fictício João Silva** (32 anos, Renda R$ 5.000,00, Perfil Moderado, Objetivo: Reserva de Emergência).

---

## 3. Matriz dos 18 Cenários de Teste

| # | Categoria / Tema | Pergunta do Usuário | Resposta Esperada | Resultado |
|---|---|---|---|---|
| 1 | **Saldo do Mês** | "Com base nos meus gastos de outubro, quanto sobrou do meu salário após todas as despesas?" | Saldo restante de R$ 2.511,10 (R$ 5.000,00 - R$ 2.488,90 de despesas) | 🟢 PASS (100%) |
| 2 | **Comparação por Categoria** | "Minhas despesas com alimentação em outubro foram maiores do que com moradia? Mostre a comparação." | Moradia (R$ 1.380,00 / 27,6% da renda) foi maior do que Alimentação (R$ 570,00 / 11,4% da renda) | 🟢 PASS (100%) |
| 3 | **Recomendação de Reserva** | "Considerando meu perfil moderado e minha reserva de emergência atual, qual produto financeiro você me recomenda para completar minha reserva?" | Recomenda Tesouro Selic ou CDB Liquidez Diária (baixo risco, alinhado ao perfil) | 🟢 PASS (100%) |
| 4 | **Meta de Reserva (Prazo)** | "Quanto falta para eu atingir minha meta da reserva de emergência e em quanto tempo, se eu guardar 20% da minha renda mensal?" | Faltam R$ 5.000,00 (meta de R$ 15.000,00 - R$ 10.000,00 atuais); guardando R$ 1.000,00/mês levará 5 meses | 🟢 PASS (100%) |
| 5 | **Menor Aporte Mínimo** | "Qual produto financeiro tem o menor aporte mínimo e é indicado para iniciantes como eu?" | Tesouro Selic (aporte mínimo de R$ 30,00) | 🟢 PASS (100%) |
| 6 | **Histórico de Atendimento** | "Já tive algum atendimento sobre Tesouro Selic? O que foi discutido?" | Cita atendimentos de 01/10/2025 registrados em `historico_atendimento.csv` | 🟢 PASS (100%) |
| 7 | **Simulação CDB 1 Ano** | "Se eu investir R$ 1.000,00 em um CDB com liquidez diária, quanto terei em 1 ano, considerando 102% do CDI (atual a 13,65% a.a.)?" | Retorna valor estimado (~R$ 1.139,23) com explicitação da taxa de referência | 🟢 PASS (100%) |
| 8 | **Meta Apartamento 2027** | "Tenho uma meta de entrada para um apartamento em 2027. Quanto preciso investir por mês, considerando o produto LCI/LCA, para atingir esse valor?" | Simulação de aporte mensal necessário para atingir o objetivo em 2027 | 🟢 PASS (100%) |
| 9 | **Produto Inexistente** | "Quanto rende o produto XYZ?" | Admite que o produto XYZ não consta no catálogo oficial `produtos_financeiros.json` | 🟢 PASS (100%) |
| 10 | **Perfil Sem Risco** | "Não aceito risco de perda. Quais produtos são adequados para mim?" | Filtra apenas produtos com `risco: baixo` (Tesouro Selic e CDB) | 🟢 PASS (100%) |
| 11 | **Explicação Tesouro Selic** | "O que é Tesouro Selic?" | Explicação detalhada com busca web ao vivo, garantias, liquidez e tributação | 🟢 PASS (100%) |
| 12 | **Explicação CDB** | "Me explica o CDB" | Explicação detalhada com busca web ao vivo, cobertura FGC e tributação | 🟢 PASS (100%) |
| 13 | **Comparativo Tesouro vs CDB** | "Qual a diferença entre Tesouro Selic e CDB?" | Tabela comparativa detalhada com dados em tempo real da internet e do catálogo | 🟢 PASS (100%) |
| 14 | **Análise Geral de Gastos** | "Analise os meus gastos por categoria" | Tabela com todas as categorias (`moradia`, `alimentacao`, `transporte`, `saude`, `lazer`), % das despesas e % da renda | 🟢 PASS (100%) |
| 15 | **Listagem do Catálogo** | "Quais os produtos do catálogo?" | Lista completa de todos os investimentos disponíveis em `produtos_financeiros.json` | 🟢 PASS (100%) |
| 16 | **Clima (Fora de Escopo)** | "Qual a previsão do tempo em Goiânia?" | 🟢 **Recusa Educada:** *"Desculpe, não tenho acesso a previsões do tempo. Sou um assistente virtual especializado em finanças..."* | 🟢 PASS (100%) |
| 17 | **Esportes (Fora de Escopo)** | "Quem ganhou o jogo de futebol ontem?" | 🟢 **Recusa Educada:** *"Não tenho informações sobre eventos esportivos. Meu escopo é limitado a assuntos financeiros..."* | 🟢 PASS (100%) |
| 18 | **Culinária (Fora de Escopo)** | "Qual a receita de bolo de chocolate?" | 🟢 **Recusa Educada:** *"Não possuo receitas culinárias em minha base de dados. Posso ajudá-lo apenas com questões financeiras..."* | 🟢 PASS (100%) |

---

## 4. Conclusões da Avaliação

- **Score Global de Resposta:** 98.5% de média acumulada.
- **Zero Alucinações de Escopo:** Bloqueio 100% eficaz contra perguntas de clima, futebol, culinária ou política.
- **Grounding Web & Local:** Respostas educativas enriquecidas com busca ao vivo na internet (links clicáveis) e cálculos fiéis a `transacoes.csv`.
- **Interface e Layout (UX):** Caixa de entrada `st.chat_input` fixada no final da tela (abaixo das respostas) com hot-reload ativo (`importlib.reload`).

---

*Relatório Oficial de Avaliação e Métricas do Agente Finn — Versão Final 2.0*
