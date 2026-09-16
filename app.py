import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Configuração da Página e Estética Enterprise
st.set_page_config(
    page_title="ERP BM Make Up Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada (Design System)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Integração da imagem */
    [data-testid="stImage"] img {
        mix-blend-mode: multiply;
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    /* Botões elegantes */
    .stButton>button {
        background: linear-gradient(135deg, #d91c84 0%, #b01269 100%);
        color: white; border-radius: 8px; padding: 0.6rem 1.2rem; font-weight: 600; border: none;
        box-shadow: 0 4px 12px rgba(217, 28, 132, 0.2); transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #b01269 0%, #8c0d52 100%);
        box-shadow: 0 6px 15px rgba(217, 28, 132, 0.35);
    }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px;
        border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetric"] label { color: #64748b !important; font-weight: 500; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #d91c84 !important; font-weight: 700; }
    h1, h2, h3 { color: #1e293b; font-weight: 700; margin-bottom: 0px; padding-bottom: 0px;}
    </style>
""", unsafe_allow_html=True)

# Motor de busca inteligente da Logo
@st.cache_resource
def encontrar_caminho_logo():
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    for arquivo in ["logo.png", "logo.png.png", "logo.jpg", "logo.jpeg"]:
        caminho = os.path.join(pasta_atual, arquivo)
        if os.path.exists(caminho):
            return caminho
    return None

caminho_oficial_logo = encontrar_caminho_logo()

# Integração Nativa da Logo no Sistema (Canto superior esquerdo padrão SaaS)
if caminho_oficial_logo:
    try:
        st.logo(caminho_oficial_logo)
    except:
        pass

# 2. Sistema de Autenticação
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if caminho_oficial_logo:
            st.image(caminho_oficial_logo, width=180)
            
        st.markdown("<h2 style='color: #d91c84;'>ERP BM Make Up</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 18px; margin-top: 5px; margin-bottom: 20px; color: #64748b;'>Acesso Restrito ao Sistema</h3>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            botao_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if botao_login:
                if usuario == "admin" and senha == "bmstore2026":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# 3. Inicialização de Dados Limpos
if 'produtos' not in st.session_state:
    st.session_state.produtos = pd.DataFrame(columns=["SKU", "Produto", "Custo (R$)", "Preço Venda (R$)", "Taxa ML (%)", "Frete Médio (R$)", "Estoque"])

if 'vendas' not in st.session_state:
    st.session_state.vendas = pd.DataFrame(columns=["Data", "SKU", "Produto", "Qtd", "Preço Unit", "Custo Unit", "Taxa ML", "Frete"])

# 4. Barra Lateral de Navegação
st.sidebar.markdown("<h3 style='text-align: center; color: #d91c84; font-size: 22px; margin-top: 10px;'>ERP BM Make Up</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Navegação Principal", ["Dashboard Executivo", "Cadastrar / Listar Produtos", "Registrar Venda", "Simulador de Lucro por Venda", "Controle de Estoque"])
st.sidebar.markdown("---")
if st.sidebar.button("Sair / Logout", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# Função auxiliar para a Headline perfeitamente alinhada
def exibir_headline(titulo_pagina, subtitulo):
    col_logo, col_texto = st.columns([1, 8], vertical_alignment="center")
    
    with col_logo:
        if caminho_oficial_logo:
            st.image(caminho_oficial_logo, use_container_width=True)
            
    with col_texto:
        st.markdown("<span style='color: #d91c84; font-weight: bold; font-size: 14px;'>ERP BM MAKE UP STORE</span>", unsafe_allow_html=True)
        st.title(titulo_pagina)
        st.markdown(f"<p style='color: #64748b; font-size: 16px; margin-top: -10px;'>{subtitulo}</p>", unsafe_allow_html=True)
    st.markdown("---")

# 5. Módulos do Sistema
if menu == "Dashboard Executivo":
    exibir_headline("Dashboard Executivo", "Desempenho financeiro, faturamento e lucratividade da loja.")
    
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        filtro_periodo = st.selectbox("Selecione o Intervalo", ["Últimos 7 dias", "Últimos 14 dias", "Últimos 30 dias", "Personalizado"])
    
    hoje = datetime.now()
    if filtro_periodo == "Últimos 7 dias": data_inicio = hoje - timedelta(days=7)
    elif filtro_periodo == "Últimos 14 dias": data_inicio = hoje - timedelta(days=14)
    elif filtro_periodo == "Últimos 30 dias": data_inicio = hoje - timedelta(days=30)
    else:
        with col_f2:
            datas_pers = st.date_input("Selecione o Período", [hoje - timedelta(days=30), hoje])
            if len(datas_pers) == 2:
                data_inicio = datetime.combine(datas_pers[0], datetime.min.time())
                hoje = datetime.combine(datas_pers[1], datetime.max.time())
            else:
                data_inicio = hoje - timedelta(days=30)

    # Lógica do Período Anterior para Comparação (Deltas)
    dias_delta = (hoje - data_inicio).days
    if dias_delta <= 0: dias_delta = 1
    
    data_fim_anterior = data_inicio - timedelta(seconds=1)
    data_inicio_anterior = data_fim_anterior - timedelta(days=dias_delta)

    df_vendas = st.session_state.vendas
    if not df_vendas.empty:
        df_vendas["Data"] = pd.to_datetime(df_vendas["Data"])
        df_atual = df_vendas[(df_vendas["Data"] >= data_inicio) & (df_vendas["Data"] <= hoje)]
        df_ant = df_vendas[(df_vendas["Data"] >= data_inicio_anterior) & (df_vendas["Data"] <= data_fim_anterior)]
    else:
        df_atual = pd.DataFrame(columns=["Data", "SKU", "Qtd", "Preço Unit", "Custo Unit", "Taxa ML", "Frete"])
        df_ant = pd.DataFrame(columns=["Data", "SKU", "Qtd", "Preço Unit", "Custo Unit", "Taxa ML", "Frete"])

    # Cálculos Período Atual
    fat_atual = (df_atual["Qtd"] * df_atual["Preço Unit"]).sum() if not df_atual.empty else 0.0
    custos_atual = ((df_atual["Qtd"] * df_atual["Custo Unit"]) + (df_atual["Qtd"] * df_atual["Taxa ML"]) + (df_atual["Qtd"] * df_atual["Frete"])).sum() if not df_atual.empty else 0.0
    lucro_atual = fat_atual - custos_atual
    margem_atual = (lucro_atual / fat_atual * 100) if fat_atual > 0 else 0.0
    vendas_atual = df_atual['Qtd'].sum() if not df_atual.empty else 0
    skus_atual = len(st.session_state.produtos)

    # Cálculos Período Anterior
    fat_ant = (df_ant["Qtd"] * df_ant["Preço Unit"]).sum() if not df_ant.empty else 0.0
    custos_ant = ((df_ant["Qtd"] * df_ant["Custo Unit"]) + (df_ant["Qtd"] * df_ant["Taxa ML"]) + (df_ant["Qtd"] * df_ant["Frete"])).sum() if not df_ant.empty else 0.0
    lucro_ant = fat_ant - custos_ant
    margem_ant = (lucro_ant / fat_ant * 100) if fat_ant > 0 else 0.0
    vendas_ant = df_ant['Qtd'].sum() if not df_ant.empty else 0
    skus_ant = skus_atual 

    # Função para formatar o Delta
    def calc_delta(atual, anterior, format_pct=True):
        if anterior == 0: return f"{100.0:.1f}%" if atual > 0 else "0.0%"
        var = ((atual - anterior) / anterior) * 100
        return f"{var:.1f}%" if format_pct else var

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Exibição dos KPIs (6 Cards)
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento Total", f"R$ {fat_atual:,.2f}", calc_delta(fat_atual, fat_ant))
    k2.metric("Lucro Total", f"R$ {lucro_atual:,.2f}", calc_delta(lucro_atual, lucro_ant))
    k3.metric("Margem de Lucro Média", f"{margem_atual:.1f}%", calc_delta(margem_atual, margem_ant))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    k4, k5, k6 = st.columns(3)
    k4.metric("Total de Custos", f"R$ {custos_atual:,.2f}", calc_delta(custos_atual, custos_ant), delta_color="inverse")
    k5.metric("Volume de Vendas", f"{vendas_atual} un", calc_delta(vendas_atual, vendas_ant))
    k6.metric("Total de SKUs Ativos", f"{skus_atual}", "0.0%", delta_color="off")

    st.markdown("<br>---<br>", unsafe_allow_html=True)
    st.subheader("📋 Histórico de Vendas no Período")
    if not df_atual.empty:
        df_exibicao = df_atual.copy()
        df_exibicao["Faturamento"] = df_exibicao["Qtd"] * df_exibicao["Preço Unit"]
        df_exibicao["Lucro Líquido"] = (df_exibicao["Qtd"] * df_exibicao["Preço Unit"]) - ((df_exibicao["Qtd"] * df_exibicao["Custo Unit"]) + (df_exibicao["Qtd"] * df_exibicao["Taxa ML"]) + (df_exibicao["Qtd"] * df_exibicao["Frete"]))
        st.dataframe(df_exibicao[["Data", "Produto", "Qtd", "Faturamento", "Lucro Líquido"]], use_container_width=True)
    else:
        st.info("Nenhuma venda registrada neste período. O histórico está limpo.")

elif menu == "Cadastrar / Listar Produtos":
    exibir_headline("Gerenciamento de Produtos", "Cadastre novos itens informando os custos de aquisição e precificação.")
    with st.form("form_produto"):
        col1, col2, col3 = st.columns(3)
        with col1:
            sku = st.text_input("SKU / Código do Produto")
            nome = st.text_input("Nome do Produto")
        with col2:
            custo = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
            preco_venda = st.number_input("Preço de Venda no ML (R$)", min_value=0.0, format="%.2f")
        with col3:
            taxa_ml = st.number_input("Taxa Média do ML (%)", value=16.0, min_value=0.0)
            frete_medio = st.number_input("Custo Fixo / Frete (R$)", value=0.0, min_value=0.0)
            estoque = st.number_input("Estoque Inicial", min_value=0, value=10, step=1)
            
        if st.form_submit_button("Salvar Novo Produto") and sku and nome:
            novo_dado = pd.DataFrame({"SKU": [sku], "Produto": [nome], "Custo (R$)": [custo], "Preço Venda (R$)": [preco_venda], "Taxa ML (%)": [taxa_ml], "Frete Médio (R$)": [frete_medio], "Estoque": [estoque]})
            st.session_state.produtos = pd.concat([st.session_state.produtos, novo_dado], ignore_index=True)
            st.success(f"Produto '{nome}' cadastrado!")
            st.rerun()

    st.subheader("Catálogo de Produtos")
    if not st.session_state.produtos.empty:
        st.dataframe(st.session_state.produtos, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

elif menu == "Registrar Venda":
    exibir_headline("Registrar Nova Venda", "Registre vendas para alimentar o Dashboard Executivo e dar baixa no estoque.")
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos primeiro.")
    else:
        with st.form("form_venda"):
            prod_vendido = st.selectbox("Escolha o Produto", st.session_state.produtos["Produto"].tolist())
            qtd_vendida = st.number_input("Quantidade Vendida", min_value=1, value=1, step=1)
            data_venda = st.date_input("Data da Venda", datetime.now())
            
            if st.form_submit_button("Confirmar e Registrar Venda"):
                p_info = st.session_state.produtos[st.session_state.produtos["Produto"] == prod_vendido].iloc[0]
                nova_venda = pd.DataFrame([{
                    "Data": datetime.combine(data_venda, datetime.min.time()), "SKU": p_info["SKU"], "Produto": prod_vendido,
                    "Qtd": qtd_vendida, "Preço Unit": p_info["Preço Venda (R$)"], "Custo Unit": p_info["Custo (R$)"],
                    "Taxa ML": p_info["Preço Venda (R$)"] * (p_info["Taxa ML (%)"] / 100), "Frete": p_info["Frete Médio (R$)"]
                }])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Produto"] == prod_vendido, "Estoque"] -= qtd_vendida
                st.success(f"Venda registrada! Estoque atualizado.")

elif menu == "Simulador de Lucro por Venda":
    exibir_headline("Simulador de Lucro Real", "Análise detalhada descontando comissões do marketplace, frete e custos de produto.")
    
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos primeiro na aba de Cadastro para realizar simulações.")
    else:
        produto_selecionado = st.selectbox("Selecione o Produto", st.session_state.produtos["Produto"].tolist())
        prod_data = st.session_state.produtos[st.session_state.produtos["Produto"] == produto_selecionado].iloc[0]
        
        preco = prod_data["Preço Venda (R$)"]
        custo = prod_data["Custo (R$)"]
        taxa_ml_pct = prod_data["Taxa ML (%)"] / 100
        frete = prod_data["Frete Médio (R$)"]
        
        valor_taxa_ml = preco * taxa_ml_pct
        lucro_bruto = preco - custo - valor_taxa_ml - frete
        margem_lucro = (lucro_bruto / preco * 100) if preco > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço de Venda", f"R$ {preco:.2f}")
        col2.metric("Custo de Aquisição", f"R$ {custo:.2f}")
        col3.metric("Taxa ML + Frete", f"R$ {(valor_taxa_ml + frete):.2f}")
        col4.metric("Lucro Líquido Real", f"R$ {lucro_bruto:.2f}", f"{margem_lucro:.1f}%")
        
        if margem_lucro < 10:
            st.error("⚠️ Atenção: Sua margem de lucro está abaixo de 10%. Risco operacional elevado!")
        elif margem_lucro >= 20:
            st.success("✅ Margem de lucro saudável e dentro do planejado!")

elif menu == "Controle de Estoque":
    exibir_headline("Gestão de Estoque", "Acompanhe o saldo físico dos produtos.")
    if not st.session_state.produtos.empty:
        st.dataframe(st.session_state.produtos[["SKU", "Produto", "Estoque"]], use_container_width=True)
        baixo_estoque = st.session_state.produtos[st.session_state.produtos["Estoque"] <= 3]
        if not baixo_estoque.empty:
            st.warning("⚠️ Alerta: Produtos com estoque crítico:")
            st.table(baixo_estoque[["SKU", "Produto", "Estoque"]])
    else:
        st.info("Estoque vazio.")