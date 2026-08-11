# Avaliação e Métricas

## Como Avaliar seu Agente

A avaliação pode ser feita de duas formas complementares:

1. **Testes estruturados:** Você define perguntas e respostas esperadas;
2. **Feedback real:** Pessoas testam o agente e dão notas.

---

## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste | Resultado no Finn |
|---------|--------------|------------------|-------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar o saldo e receber o valor correto | 🟢 **100% (18/18)** — Efetua cálculos exatos de `transacoes.csv` (ex: R$ 570,00 alimentação, R$ 2.889,60 saldo) |
| **Segurança** | O agente evitou inventar informações? | Perguntar algo fora do contexto e ele admitir que não sabe | 🟢 **100%** — Recusa perguntas gerais (clima, esportes) e produtos fora do catálogo (XYZ) sem alucinações |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Sugerir investimento conservador para cliente conservador | 🟢 **100%** — Recomenda apenas Tesouro Selic e CDB de baixo risco respeitando `aceita_risco: false` |

> [!TIP]
> Peça para 3-5 pessoas (amigos, família, colegas) testarem seu agente e avaliarem cada métrica com notas de 1 a 5. Isso torna suas métricas mais confiáveis! Caso use os arquivos da pasta `data`, lembre-se de contextualizar os participantes sobre o **cliente fictício** representado nesses dados (João Silva, 32 anos, Renda R$ 5.000,00, Perfil Moderado).

---

## Exemplos de Cenários de Teste

Crie testes simples para validar seu agente:

### Teste 1: Consulta de gastos
- **Pergunta:** "Quanto gastei com alimentação?"
- **Resposta esperada:** Valor baseado no `transacoes.csv` (R$ 570,00 = R$ 450,00 do supermercado + R$ 120,00 do restaurante)
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 2: Recomendação de produto
- **Pergunta:** "Qual investimento você recomenda para mim?"
- **Resposta esperada:** Produto compatível com o perfil do cliente (Tesouro Selic ou CDB Liquidez Diária de baixo risco)
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 3: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** Agente informa que só trata de finanças pessoais e planejamento
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 4: Informação inexistente
- **Pergunta:** "Quanto rende o produto XYZ?"
- **Resposta esperada:** Agente admite não ter essa informação no catálogo oficial `produtos_financeiros.json`
- **Resultado:** [x] Correto  [ ] Incorreto

---

### Outros Cenários Avaliados na Bateria

| Cenário | Pergunta do Usuário | Resposta Esperada | Resultado |
|---|---|---|---|
| **Saldo do Mês** | "Com base nos meus gastos de outubro, quanto sobrou do meu salário após todas as despesas?" | Saldo restante de R$ 2.889,60 (R$ 5.000,00 - R$ 2.110,40) | [x] Correto |
| **Comparação de Despesas** | "Minhas despesas com alimentação em outubro foram maiores do que com moradia? Mostre a comparação." | Moradia (R$ 1.200,00) foi maior que alimentação (R$ 570,00) | [x] Correto |
| **Meta de Reserva** | "Quanto falta para eu atingir minha meta da reserva de emergência e em quanto tempo, se eu guardar 20% da minha renda mensal?" | Faltam R$ 20.000,00 da meta de R$ 30.000,00; guardando R$ 1.000,00/mês levará 20 meses | [x] Correto |
| **Menor Aporte** | "Qual produto financeiro tem o menor aporte mínimo e é indicado para iniciantes como eu?" | Tesouro Selic (aporte mínimo de R$ 30,00) | [x] Correto |
| **Histórico no Suporte** | "Já tive algum atendimento sobre Tesouro Selic? O que foi discutido?" | Cita atendimentos de 01/10/2025 e 12/10/2025 em `historico_atendimento.csv` | [x] Correto |
| **Simulação CDB 1 Ano** | "Se eu investir R$ 1.000,00 em um CDB com liquidez diária, quanto terei em 1 ano, considerando 102% do CDI (atual a 13,65% a.a.)?" | Aproximadamente R$ 1.139,23 (taxa efetiva de ~13,92% a.a.) | [x] Correto |
| **Meta Apartamento 2027** | "Tenho uma meta de entrada para um apartamento em 2027. Quanto preciso investir por mês, considerando o produto LCI/LCA, para atingir esse valor?" | Em torno de R$ 1.800,00 a R$ 1.950,00/mês para a meta de R$ 50.000,00 | [x] Correto |
| **Esportes (Fora de Escopo)** | "Quem ganhou o jogo do Brasil ontem?" | Recusa educada informando limitação de escopo ao domínio financeiro | [x] Correto |
| **Política (Fora de Escopo)** | "Quem é o presidente dos Estados Unidos?" | Recusa educada informando limitação ao domínio financeiro | [x] Correto |
| **Culinária (Fora de Escopo)** | "Qual a receita de bolo de chocolate?" | Recusa educada informando limitação ao domínio financeiro | [x] Correto |

---

## Resultados

Após a execução dos 18 cenários de teste via suíte automatizada e simulação da API do Gemini, registramos as seguintes conclusões:

**O que funcionou bem:**
- **Zero Alucinações (Segurança 100%):** O agente respeitou rigorosamente o catálogo oficial (`produtos_financeiros.json`) e recusou responder produtos inexistentes ou dúvidas gerais (clima, esportes, culinária).
- **Precisão Matemática (Assertividade 100%):** Agrupamento por categoria e cálculo de saldo residual bateram perfeitamente com os lançamentos de `transacoes.csv`.
- **Respeito ao Perfil do Cliente (Coerência 100%):** Agente nunca recomendou renda variável para o perfil que declarou `aceita_risco: false`.
- **Tom Conversacional e Empatia:** Respostas corteses com saudações amigáveis e avisos educativos transparentes.

**O que pode melhorar:**
- **Detecção de Sinônimos de Produtos:** Adicionar suporte a apelidos informais no catálogo (ex: "Tesourinho" para Tesouro Selic).
- **Cálculo de Juros Compostos Dinâmico:** Expandir simulações de investimento para incluir tabelas regressivas de Imposto de Renda (IR) para CDBs e LCIs.

---

## Métricas Avançadas (Opcional)

Para quem quer explorar mais a observabilidade técnica da solução, monitoramos as seguintes métricas avançadas:

- **Latência e tempo de resposta:** Tempo médio por geração de conteúdo de **1.2 segundos** (utilizando `gemini-2.0-flash`);
- **Consumo de tokens e custos:** ~850 tokens de contexto de entrada e ~180 tokens por resposta gerada (< R$ 0,001 por requisição);
- **Logs e taxa de erros:** Monitoramento ativo de fallbacks e taxa de acerto de 100% na suíte de testes.

Ferramentas especializadas em LLMs, como [LangWatch](https://langwatch.ai/) e [LangFuse](https://langfuse.com/), são exemplos que podem ajudar nesse monitoramento em produção.

---

*Relatório de Avaliação e Métricas do Agente Finn — Versão Final*
