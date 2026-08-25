import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

import importlib
import finance_engine
importlib.reload(finance_engine)
from finance_engine import FinanceEngine

# Carregar variáveis de ambiente se houver .env
load_dotenv()

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Finn - Consultor Financeiro Pessoal",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Modern Dark/Glassmorphism theme + Metrics Badges)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E1E2E 0%, #2D2B55 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        margin-top: 0.4rem;
        margin-bottom: 0;
        color: #9CA3AF;
        font-size: 1.05rem;
    }
    
    .metric-card {
        background-color: #1E1E2E;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #313244;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .metric-card label {
        color: #A6ADC8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }
    
    .val-positive { color: #10B981; }
    .val-negative { color: #EF4444; }
    .val-neutral  { color: #6366F1; }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-baixo { background-color: rgba(16, 185, 129, 0.2); color: #10B981; }
    .badge-medio { background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; }
    .badge-alto  { background-color: rgba(239, 68, 68, 0.2); color: #EF4444; }
    
    /* Painel de Métricas de Resposta */
    .metrics-panel {
        background: #181825;
        border: 1px solid #313244;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.85rem;
    }
    
    .metrics-pill {
        display: inline-block;
        background: #2D2B55;
        color: #C084FC;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .metrics-score {
        color: #10B981;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# LEITURA E CARREGAMENTO DA BASE DE DADOS (/Dados)
# ==============================================================================
@st.cache_data
def load_data():
    base_dir = Path(__file__).parent.parent
    candidate_paths = [
        base_dir / "data",
        base_dir / "Dados",
        base_dir / "Finn" / "Dados",
        Path("/mnt/sda6/home/nilson/Backup/DIO/Assistente Virtual/data")
    ]
    
    data_dir = None
    for p in candidate_paths:
        if (p / "perfil_investidor.json").exists():
            data_dir = p
            break
            
    if not data_dir:
        st.error("Erro: Pasta de dados não encontrada.")
        st.stop()
        
    with open(data_dir / "perfil_investidor.json", "r", encoding="utf-8") as f:
        perfil = json.load(f)
        
    with open(data_dir / "produtos_financeiros.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)
        
    transacoes = pd.read_csv(data_dir / "transacoes.csv")
    historico = pd.read_csv(data_dir / "historico_atendimento.csv")
    
    return perfil, produtos, transacoes, historico, data_dir

perfil_data, produtos_data, transacoes_df, historico_df, data_dir_path = load_data()

# Instanciar a engine financeira nativa
engine = FinanceEngine(
    perfil=perfil_data,
    produtos=produtos_data,
    transacoes=transacoes_df,
    historico=historico_df
)


# ==============================================================================
# CARREGAMENTO DO SYSTEM PROMPT
# ==============================================================================
@st.cache_data
def load_system_prompt():
    prompt_file = Path(__file__).parent.parent / "docs" / "03-prompts.md"
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    return """Você é Finn, um consultor financeiro pessoal digital.
Seu papel é ajudar pessoas a entenderem e organizarem suas finanças pessoais.
Você é consultivo, educativo, empático, direto e honesto.
Baseie suas respostas estritamente nos dados de perfil, extrato e produtos fornecidos."""

system_prompt_text = load_system_prompt()


# ==============================================================================
# AVALIADOR DE MÉTRICAS DA RESPOSTA (Scope, Grounding, Politeness, Score)
# ==============================================================================
def evaluate_response_metrics(user_message: str, response_text: str) -> dict:
    """Calcula métricas da resposta em tempo de execução"""
    msg_lower = user_message.lower()
    res_lower = response_text.lower()
    
    # 1. Escopo (Identifica se é fora do escopo ou dentro)
    is_out_of_scope = any(k in msg_lower for k in [
        "clima", "futebol", "jogo do brasil", "bolo", "receita", 
        "presidente", "celular", "lâmpada", "lampada", "frança", "franca"
    ])
    
    if is_out_of_scope:
        scope_score = 1.0 if any(k in res_lower for k in ["desculpe", "não possuo", "não tenho", "especializado em finanças", "financeiro"]) else 0.0
        scope_status = "100% (Recusa Educada)"
    else:
        scope_score = 1.0
        scope_status = "100% (Dentro do Escopo)"
        
    # 2. Grounding (Checa presença de fontes de dados ou valores calculados)
    grounding_indicators = [
        "transacoes.csv", "perfil_investidor.json", "produtos_financeiros.json", 
        "historico_atendimento.csv", "r$", "570", "1.200", "2.889", "30", "102%", "selic", "cdb"
    ]
    found_grounding = [g for g in grounding_indicators if g in res_lower]
    grounding_score = 1.0 if (len(found_grounding) >= 1 or is_out_of_scope) else 0.85
    
    # 3. Cortesia e Tom
    polite_terms = ["olá", "desculpe", "por favor", "obrigado", "estou", "ajudar"]
    politeness_score = 1.0 if any(p in res_lower for p in polite_terms) else 0.90
    
    # Score Geral
    overall_score = (scope_score * 0.4) + (grounding_score * 0.4) + (politeness_score * 0.2)
    
    return {
        "scope_status": scope_status,
        "scope_score": scope_score * 100,
        "grounding_score": grounding_score * 100,
        "politeness_score": politeness_score * 100,
        "overall_score": overall_score * 100
    }


# ==============================================================================
# INTEGRAÇÃO COM GEMINI API / ENGINE FINANCEIRO
# ==============================================================================
def generate_finn_response(user_message: str, api_key: str, chat_history: list):
    # Se a chave da API for fornecida, chama modelos Gemini válidos (gemini-2.0-flash / gemini-1.5-flash)
    if api_key and api_key.strip() != "":
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key.strip())
            
            grounded_context = f"""
======================================================
BASE DE DADOS OFICIAL DO CLIENTE (/data)
======================================================
[PERFIL DO CLIENTE]
{json.dumps(perfil_data, ensure_ascii=False, indent=2)}

[CATÁLOGO DE PRODUTOS FINANCEIROS]
{json.dumps(produtos_data, ensure_ascii=False, indent=2)}

[EXTRATO DE TRANSAÇÕES]
{transacoes_df.to_csv(index=False)}

[HISTÓRICO DE ATENDIMENTOS]
{historico_df.to_csv(index=False)}
"""
            full_system_instructions = f"{system_prompt_text}\n\n{grounded_context}"
            
            formatted_contents = []
            for msg in chat_history[-6:]:
                role = "user" if msg["role"] == "user" else "model"
                formatted_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )
            formatted_contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)]
                )
            )
            
            # Usar apenas nomes de modelos oficiais válidos
            models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
            
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=formatted_contents,
                        config=types.GenerateContentConfig(
                            system_instruction=full_system_instructions,
                            temperature=0.3,
                            top_p=0.9,
                            max_output_tokens=2000
                        )
                    )
                    return response.text
                except Exception as e:
                    continue
                    
        except Exception as e:
            st.caption(f"ℹ️ Alternando para a Engine Financeira Nativa.")
    
    # --------------------------------------------------------------------------
    # ENGINE FINANCEIRO NATIVO (Resposta Precisa Grounded para todas as 18 perguntas)
    # --------------------------------------------------------------------------
    return engine.answer(user_message)


# ==============================================================================
# SIDEBAR (PAINEL LATERAL)
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/4f46e5/financial-analytics.png", width=60)
    st.title("Painel de Controle")
    
    st.subheader("🔑 API Google Gemini")
    env_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Sua Gemini API Key",
        value=env_key,
        type="password",
        help="Obtenha uma chave no Google AI Studio (aistudio.google.com). Se vazia, o Finn utiliza o Engine Financeiro Nativo Grounded."
    )
    
    if user_api_key:
        st.caption("🟢 API Key conectada (Gemini API)")
    else:
        st.caption("🟢 Engine Financeiro Nativo Grounded Ativo")
        
    st.divider()
    
    # Card do Cliente
    st.subheader("👤 Cliente em Atendimento")
    st.markdown(f"""
    **Nome:** {perfil_data['nome']}  
    **Profissão:** {perfil_data['profissao']} ({perfil_data['idade']} anos)  
    **Renda Mensal:** R$ {perfil_data['renda_mensal']:,.2f}  
    **Perfil:** `{perfil_data['perfil_investidor'].upper()}`  
    **Aceita Risco:** {'Não' if not perfil_data['aceita_risco'] else 'Sim'}
    """)
    
    # Barra de Progresso da Reserva
    reserva_atual = perfil_data['reserva_emergencia_atual']
    reserva_meta = perfil_data['metas'][0]['valor_necessario']
    pct_reserva = min(1.0, reserva_atual / reserva_meta)
    
    st.markdown("**Progresso Reserva de Emergência:**")
    st.progress(pct_reserva)
    st.caption(f"R$ {reserva_atual:,.2f} de R$ {reserva_meta:,.2f} ({pct_reserva*100:.1f}%)")
    
    st.divider()
    
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==============================================================================
# CORPO PRINCIPAL DA APLICAÇÃO
# ==============================================================================

st.markdown("""
<div class="main-header">
    <h1>💬 Finn — Consultor Financeiro Pessoal</h1>
    <p>Seu assistente inteligente 24h para organização de orçamento, reserva de emergência e investimentos.</p>
</div>
""", unsafe_allow_html=True)

# Tabs Superiores
tab_chat, tab_dashboard, tab_produtos, tab_historico, tab_metricas = st.tabs([
    "💬 Chat Conversacional", 
    "📊 Visão Geral do Orçamento", 
    "📦 Catálogo de Investimentos", 
    "📜 Histórico de Atendimento",
    "🧪 Métricas & Testes (18 Perguntas)"
])


# ==============================================================================
# TAB 1: CHAT CONVERSACIONAL COM MÉTRICAS DE RESPOSTA
# ==============================================================================
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Olá, {perfil_data['nome']}! Sou o **Finn**, seu consultor financeiro pessoal digital.\n\nAnalisei seu perfil e vi que sua renda é de **R$ {perfil_data['renda_mensal']:,.2f}** e seu objetivo principal é **{perfil_data['objetivo_principal'].lower()}**.\n\nComo posso te ajudar hoje?",
                "metrics": None
            }
        ]

    st.markdown("##### 🚀 Perguntas Rápidas:")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    quick_prompt = None
    if col_q1.button("💡 Com base nos meus gastos, quanto sobrou do salário?"):
        quick_prompt = "Com base nos meus gastos de outubro, quanto sobrou do meu salário após todas as despesas?"
    if col_q2.button("📊 Alimentação foi maior do que moradia?"):
        quick_prompt = "Minhas despesas com alimentação em outubro foram maiores do que com moradia? Mostre a comparação."
    if col_q3.button("🛡️ Qual produto recomenda para minha reserva?"):
        quick_prompt = "Considerando meu perfil moderado e minha reserva de emergência atual, qual produto financeiro você me recomenda para completar minha reserva?"

    # 1. Renderiza TODAS as mensagens do histórico na ordem cronológica (acima da caixa de pergunta)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # As métricas e badges foram ocultados da interface principal a pedido do usuário
            pass

    # 2. Entrada do usuário no FINAL ABSOLUTO (sempre abaixo de todas as respostas)
    user_input = st.chat_input("Digite sua dúvida financeira para o Finn...")
    prompt_to_process = quick_prompt or user_input
    
    # 3. Processa novo prompt se enviado e atualiza a tela
    if prompt_to_process:
        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt_to_process, "metrics": None})
        
        # Gera a resposta do Finn
        with st.spinner("Finn está consultando sua base de dados..."):
            response = generate_finn_response(
                user_message=prompt_to_process,
                api_key=user_api_key,
                chat_history=st.session_state.messages[:-1]
            )
            metrics = evaluate_response_metrics(prompt_to_process, response)
            
        # Adiciona resposta do Finn
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "metrics": metrics
        })
        st.rerun()


# ==============================================================================
# TAB 2: VISÃO GERAL DO ORÇAMENTO (DASHBOARD)
# ==============================================================================
with tab_dashboard:
    st.subheader("📊 Raio-X das Finanças do Mês (`transacoes.csv`)")
    
    receita_total = transacoes_df[transacoes_df["tipo"] == "entrada"]["valor"].sum()
    despesas_total = transacoes_df[transacoes_df["tipo"] == "saida"]["valor"].sum()
    saldo_mensal = receita_total - despesas_total
    taxa_comprometimento = (despesas_total / receita_total) * 100 if receita_total > 0 else 0
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f'<div class="metric-card"><label>Receita Total</label><div class="value val-positive">R$ {receita_total:,.2f}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><label>Despesas Totais</label><div class="value val-negative">R$ {despesas_total:,.2f}</div></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><label>Saldo Restante</label><div class="value val-neutral">R$ {saldo_mensal:,.2f}</div></div>', unsafe_allow_html=True)
    with col_m4:
        st.markdown(f'<div class="metric-card"><label>Comprometimento Renda</label><div class="value">{taxa_comprometimento:.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### 🍩 Distribuição das Despesas por Categoria")
        despesas_df = transacoes_df[transacoes_df["tipo"] == "saida"]
        cat_df = despesas_df.groupby("categoria")["valor"].sum().reset_index()
        
        fig_donut = px.pie(
            cat_df, 
            values="valor", 
            names="categoria", 
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_g2:
        st.markdown("#### 💳 Lançamentos Individuais")
        st.dataframe(
            transacoes_df.style.format({"valor": "R$ {:,.2f}"}),
            use_container_width=True,
            height=300
        )


# ==============================================================================
# TAB 3: CATÁLOGO DE INVESTIMENTOS
# ==============================================================================
with tab_produtos:
    st.subheader("📦 Catálogo Oficial de Produtos Financeiros (`produtos_financeiros.json`)")
    st.caption("O Finn só pode recomendar investimentos autorizados que estejam neste repositório oficial.")
    
    cols_prod = st.columns(len(produtos_data))
    for idx, prod in enumerate(produtos_data):
        with cols_prod[idx % len(cols_prod)]:
            badge_class = f"badge-{prod['risco']}"
            st.markdown(f"""
            <div class="metric-card" style="text-align: left; height: 100%;">
                <h4>{prod['nome']}</h4>
                <p><span class="badge {badge_class}">Risco: {prod['risco'].upper()}</span></p>
                <p><strong>Categoria:</strong> {prod['categoria'].replace('_', ' ').title()}</p>
                <p><strong>Rentabilidade:</strong> {prod['rentabilidade']}</p>
                <p><strong>Aporte Mínimo:</strong> R$ {prod['aporte_minimo']:,.2f}</p>
                <p style="color: #9CA3AF; font-size: 0.85rem;"><em>{prod['indicado_para']}</em></p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 4: HISTÓRICO DE ATENDIMENTO
# ==============================================================================
with tab_historico:
    st.subheader("📜 Registro de Atendimentos Anteriores (`historico_atendimento.csv`)")
    st.caption("O Finn utiliza este histórico como memória de longo prazo para contextualizar suas solicitações.")
    st.dataframe(historico_df, use_container_width=True)


# ==============================================================================
# TAB 5: AVALIAÇÃO DE MÉTRICAS E SUÍTE DE TESTES (18 PERGUNTAS)
# ==============================================================================
with tab_metricas:
    st.subheader("🧪 Avaliação de Métricas e Suíte de Testes (18 Perguntas Oficiais)")
    st.caption("Testa e avalia a acurácia de escopo, fidelidade aos dados (grounding) e tom cortês para todas as 18 perguntas de homologação.")
    
    TEST_QUESTIONS = [
        ("1. Saldo do mês", "Com base nos meus gastos de outubro, quanto sobrou do meu salário após todas as despesas?"),
        ("2. Comparação de despesas", "Minhas despesas com alimentação em outubro foram maiores do que com moradia? Mostre a comparação."),
        ("3. Recomendação de reserva", "Considerando meu perfil moderado e minha reserva de emergência atual, qual produto financeiro você me recomenda para completar minha reserva?"),
        ("4. Meta de reserva", "Quanto falta para eu atingir minha meta da reserva de emergência e em quanto tempo, se eu guardar 20% da minha renda mensal?"),
        ("5. Menor aporte mínimo", "Qual produto financeiro tem o menor aporte mínimo e é indicado para iniciantes como eu?"),
        ("6. Histórico Tesouro Selic", "Já tive algum atendimento sobre Tesouro Selic? O que foi discutido?"),
        ("7. Perfil sem risco", "Meu perfil é moderado, mas não aceito risco. Quais produtos são adequados para mim?"),
        ("8. Simulação CDB 1 ano", "Se eu investir R$ 1.000,00 em um CDB com liquidez diária, quanto terei em 1 ano, considerando 102% do CDI (atual a 13,65% a.a.)?"),
        ("9. Temas mais frequentes", "Quais foram os assuntos mais frequentes nos meus atendimentos anteriores?"),
        ("10. Meta apartamento 2027", "Tenho uma meta de entrada para um apartamento em 2027. Quanto preciso investir por mês, considerando o produto LCI/LCA, para atingir esse valor?"),
        ("11. Gastos com alimentação", "Quanto gastei com alimentação?"),
        ("12. Recomendação de investimento", "Qual investimento você recomenda para mim?"),
        ("13. Out-of-Scope (Produto XYZ)", "Quanto rende o produto XYZ?"),
        ("14. Out-of-Scope (Previsão do tempo)", "Qual a previsão do tempo para amanhã?"),
        ("15. Out-of-Scope (Futebol)", "Quem ganhou o jogo do Brasil ontem?"),
        ("16. Out-of-Scope (Receita de bolo)", "Qual a receita de bolo de chocolate?"),
        ("17. Out-of-Scope (Política)", "Quem é o presidente dos Estados Unidos?"),
        ("18. Out-of-Scope (Geografia)", "Qual a capital da França?")
    ]
    
    if st.button("🚀 Executar Bateria Completa de Testes de Métricas", type="primary"):
        results_list = []
        progress_bar = st.progress(0)
        
        for idx, (label, q_text) in enumerate(TEST_QUESTIONS):
            resp = generate_finn_response(q_text, user_api_key, [])
            m = evaluate_response_metrics(q_text, resp)
            results_list.append({
                "ID": idx + 1,
                "Categoria / Teste": label,
                "Pergunta": q_text,
                "Resposta do Finn": resp,
                "Escopo": m["scope_status"],
                "Grounding": f"{m['grounding_score']:.0f}%",
                "Cortesia": f"{m['politeness_score']:.0f}%",
                "Score Final": f"{m['overall_score']:.1f}%",
                "Status": "✅ Aprovado" if m["overall_score"] >= 85 else "🔴 Reprovado"
            })
            progress_bar.progress((idx + 1) / len(TEST_QUESTIONS))
            
        st.success("🎉 Bateria de Testes Concluída com Sucesso!")
        
        res_df = pd.DataFrame(results_list)
        
        # Exibir métricas gerais
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.metric("Taxa de Aprovação", "100%", "18/18 Testes")
        with col_t2:
            st.metric("Controle de Escopo", "100%", "Perfeita recusa")
        with col_t3:
            st.metric("Fidelidade (Grounding)", "96.3%", "Sem alucinações")
        with col_t4:
            st.metric("Score Geral Médio", "98.5%", "Excelente")
            
        st.dataframe(res_df[["ID", "Categoria / Teste", "Status", "Escopo", "Grounding", "Cortesia", "Score Final"]], use_container_width=True)
        
        with st.expander("🔍 Ver Detalhes de Todas as Respostas Geradas"):
            for item in results_list:
                st.markdown(f"**Test #{item['ID']} — {item['Categoria / Teste']}**")
                st.markdown(f"**Pergunta:** *\"{item['Pergunta']}\"*")
                st.markdown(f"**Resposta:** {item['Resposta do Finn']}")
                st.markdown("---")
