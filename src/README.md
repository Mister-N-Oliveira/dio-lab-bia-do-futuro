# Código da Aplicação

# 💬 Finn — Assistente Virtual de Finanças Pessoais

> **Projeto desenvolvido para o desafio da Digital Innovation One (DIO):**  
> *Criando um Assistente Virtual de Finanças com IA e Grounding em Dados.*

---

## 📌 Visão Geral

**Finn** é um consultor financeiro pessoal digital projetado para ser consultivo, educativo, empático e extremamente preciso. Diferente de chatbots comuns, o Finn opera sob **regras rígidas de anti-alucinação** e consome estritamente 4 bases de dados oficiais para fornecer diagnósticos financeiros, alertas de gastos e recomendações de investimentos alinhadas ao perfil do usuário.

---

## 🚀 Funcionalidades Principais

- 💬 **Chat Conversacional RAG:** Responde a dúvidas financeiras cruzando dados do cliente com catálogos oficiais e histórico de conversas.
- 📊 **Dashboard Financeiro Interativo:** Gráfico de rosca (Plotly) para distribuição de despesas por categoria (`moradia`, `alimentação`, `saúde`, `lazer`, etc.) e resumo de comprometimento da renda.
- 🎯 **Acompanhamento de Reserva de Emergência:** Barra de progresso visual monitorando o cumprimento da meta financeira atual.
- 📦 **Catálogo Oficial de Investimentos:** Filtro e exibição dos produtos autorizados (Tesouro Selic, CDB, LCI/LCA, FIIs, etc.).
- 🛡️ **Grounding e Anti-Alucinação:** Respostas fundamentadas estritamente nas tabelas oficiais de `/Dados`. Caso não possua dados ou a dúvida fuja do escopo, o Finn declara honestamente e sugere o redirecionamento adequado.

---

## 📁 Estrutura do Repositório

```text
.
├── app.py                      # Aplicação web principal em Streamlit
├── requirements.txt            # Dependências da aplicação Python
├── .env.example                # Modelo de configuração da API Key
├── README.md                   # Documentação do projeto
├── Dados/                      # Base de Conhecimento do Cliente
│   ├── perfil_investidor.json  # Dados cadastrais e perfil de risco
│   ├── produtos_financeiros.json # Catálogo oficial de investimentos
│   ├── transacoes.csv          # Extrato recente de receitas e despesas
│   └── historico_atendimento.csv # Memória de atendimentos anteriores
└── Finn/
    ├── Dados/                  # Cópia de segurança dos dados
    └── GitHub/                 # Documentação técnica completa
        ├── agente_financeiro_design.md  # Especificação da persona e arquitetura
        ├── finn_system_prompt.md        # Prompt do sistema com poucas demonstrações (Few-Shot)
        └── finn_knowledge_base.md       # Esquema detalhado da base de conhecimento
```

---

## 🛠️ Como Executar a Aplicação Localmente

### 1. Pré-requisitos
Possuir o **Python 3.10** ou superior instalado no seu sistema.

### 2. Criar e Ativar um Ambiente Virtual
```bash
# No Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# No Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar a Chave da API Gemini (Opcional)
Renomeie ou crie um arquivo `.env` na raiz do projeto com sua chave obtida no [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=sua_chave_api_aqui
```
> *Nota: Se você não preencher uma chave de API, a aplicação executará no **Modo Simulação / Grounding Local**, mantendo toda a interatividade e fundamentação de dados.*

### 5. Iniciar o Streamlit
```bash
streamlit run app.py
```
Acesse `http://localhost:8501` no seu navegador!

---

## 🧠 Arquitetura e Engenharia de Prompt (Few-Shot)

O Finn foi construído aplicando técnicas consolidadas de **Engenharia de Prompt**:
- **System Instructions:** Definem limites de atuação (não faz IR, não atua como advogado, não faz previsão de mercado).
- **Few-Shot Prompts:** Demonstrações dentro do System Prompt ([finn_system_prompt.md](file:///mnt/sda6/home/nilson/Backup/DIO/Assistente%20Virtual/Finn/GitHub/finn_system_prompt.md)) que ensinam o modelo a cruzar `perfil_investidor.json` com `produtos_financeiros.json` e `transacoes.csv`.

---

## 📜 Licença

Projeto desenvolvido para fins educacionais no âmbito da **Digital Innovation One (DIO)**.
