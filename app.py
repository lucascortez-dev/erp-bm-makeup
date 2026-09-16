import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client, Client

# Configuração da Conexão com o Supabase (Certifique-se de usar a URL raiz terminada em .co)
SUPABASE_URL = "https://gcjyhaamliodpcdphwsg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInI1cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjanloYWFtbGlvZHBjZHBod3NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEwMzU5ODEsImV4cCI6MjA1NjYxMTk4MX0.RuBIOfGCS7DxhfRNGLtRogLmhNmUhLb7GMWF-8bZSI6ImFub24iLCJPY3A3MiwzMDIzM01Myv4cCI6MjNlNW1TMMyNhQ"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

# 1. Configuração da Página e Estética Enterprise
st.set_page_config(
    page_title="ERP BM Make Up Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    [data-testid="stImage"] img { mix-blend-mode: multiply; border-radius: 8px; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    div.row-widget.stRadio > div { background-color: #ffffff; border-radius: 8px; padding: 10px; }
    .stButton>button {
        background: linear-gradient(135deg, #d91c84 0%, #b01269 100%);
        color: white; border-radius: 8px; padding: 0.6rem 1.2rem; font-weight: 600; border: none;
        box-shadow: 0 4px 12px rgba(217, 28, 132, 0.2); transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #b01269 0%, #8c0d52 100%);
        box-shadow: 0 6px 15px rgba(217, 28, 132, 0.35);
    }
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

# Funções de Leitura Protegidas com Tratamento de Erro
def carregar_produtos():
    if not supabase:
        return pd.DataFrame(columns=["sku", "produto", "custo", "preco_venda", "taxa_ml", "frete_medio", "estoque"])
    try:
        response = supabase.table("produtos").select("*").execute()
        data = response.data
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"Aviso de conexão com o banco de produtos: {e}")
    return pd.DataFrame(columns=["sku", "produto", "custo", "preco_venda", "taxa_ml", "frete_medio", "estoque"])

def carregar_vendas():
    if not supabase:
        return pd.DataFrame(columns=["id", "data", "sku", "produto", "qtd", "pagamento", "preco_unit", "custo_unit", "taxa_ml", "frete"])
    try:
        response = supabase.table("vendas").select("*").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            if not df.empty and "data" in df.columns:
                df["data"] = pd.to_datetime(df["data"])
            return df
    except Exception as e:
        st.warning(f"Aviso de conexão com o banco de vendas: {e}")
    return pd.DataFrame(columns=["id", "data", "sku", "produto", "qtd", "pagamento", "preco_unit", "custo_unit", "taxa_ml", "frete"])

# 4. Barra Lateral de Navegação
st.sidebar.markdown("<h3 style='text-align: center; color: #d91c84; font-size: 22px; margin-top: 10px;'>ERP BM Make Up</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação Principal", ["Dashboard Executivo", "Cadastrar / Listar Produtos", "Registrar Venda", "Simulador de Lucro por Venda", "Controle de Estoque"])
st.sidebar.markdown("---")
if st.sidebar.button("Sair / Logout", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

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

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 5. Módulos do Sistema
df_produtos = carregar_produtos()
df_vendas = carregar_vendas()

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

    dias_delta = (hoje - data_inicio).days
    if dias_delta <= 0: dias_delta = 1
    
    data_fim_anterior = data_inicio - timedelta(seconds=1)
    data_inicio_anterior = data_fim_anterior - timedelta(days=dias_delta)

    if not df_vendas.empty:
        df_atual = df_vendas[(df_vendas["data"] >= data_inicio) & (df_vendas["data"] <= hoje)]
        df_ant = df_vendas[(df_vendas["data"] >= data_inicio_anterior) & (df_vendas["data"] <= data_fim_anterior)]
    else:
        df_atual = pd.DataFrame(columns=["data", "sku", "qtd", "pagamento", "preco_unit", "custo_unit", "taxa_ml", "frete"])
        df_ant = pd.DataFrame(columns=["data", "sku", "qtd", "pagamento", "preco_unit", "custo_unit", "taxa_ml", "frete"])

    fat_atual = (df_atual["qtd"] * df_atual["preco_unit"]).sum() if not df_atual.empty else 0.0
    custos_atual = ((df_atual["qtd"] * df_atual["custo_unit"]) + (df_atual["qtd"] * df_atual["taxa_ml"]) + (df_atual["qtd"] * df_atual["frete"])).sum() if not df_atual.empty else 0.0
    lucro_atual = fat_atual - custos_atual
    margem_atual = (lucro_atual / fat_atual * 100) if fat_atual > 0 else 0.0
    vendas_atual = df_atual['qtd'].sum() if not df_atual.empty else 0
    skus_atual = len(df_produtos)

    fat_ant = (df_ant["qtd"] * df_ant["preco_unit"]).sum() if not df_ant.empty else 0.0
    custos_ant = ((df_ant["qtd"] * df_ant["custo_unit"]) + (df_ant["qtd"] * df_ant["taxa_ml"]) + (df_ant["qtd"] * df_ant["frete"])).sum() if not df_ant.empty else 0.0
    lucro_ant = fat_ant - custos_ant
    margem_ant = (lucro_ant / fat_ant * 100) if fat_ant > 0 else 0.0
    vendas_ant = df_ant['qtd'].sum() if not df_ant.empty else 0

    def calc_delta(atual, anterior):
        if anterior == 0: return f"{100.0:.1f}%" if atual > 0 else "0.0%"
        var = ((atual - anterior) / anterior) * 100
        return f"{var:.1f}%"

    st.markdown("<br>", unsafe_allow_html=True)
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Faturamento Total", formatar_moeda(fat_atual), calc_delta(fat_atual, fat_ant))
    k2.metric("Lucro Total", formatar_moeda(lucro_atual), calc_delta(lucro_atual, lucro_ant))
    k3.metric("Margem de Lucro Média", f"{margem_atual:.1f}%", calc_delta(margem_atual, margem_ant))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    k4, k5, k6 = st.columns(3)
    k4.metric("Total de Custos", formatar_moeda(custos_atual), calc_delta(custos_atual, custos_ant), delta_color="inverse")
    k5.metric("Volume de Vendas", f"{vendas_atual} un", calc_delta(vendas_atual, vendas_ant))
    k6.metric("Total de SKUs Ativos", f"{skus_atual}", "0.0%", delta_color="off")

    st.markdown("<br>---<br>", unsafe_allow_html=True)
    st.subheader("📋 Histórico de Vendas no Período")
    if not df_atual.empty:
        df_exibicao = df_atual.copy()
        df_exibicao["Data"] = df_exibicao["data"].dt.strftime('%d/%m/%Y')
        df_exibicao["Faturamento"] = (df_exibicao["qtd"] * df_exibicao["preco_unit"]).apply(formatar_moeda)
        df_exibicao["Lucro Líquido"] = ((df_exibicao["qtd"] * df_exibicao["preco_unit"]) - ((df_exibicao["qtd"] * df_exibicao["custo_unit"]) + (df_exibicao["qtd"] * df_exibicao["taxa_ml"]) + (df_exibicao["qtd"] * df_exibicao["frete"]))).apply(formatar_moeda)
        
        st.dataframe(df_exibicao[["Data", "produto", "qtd", "pagamento", "Faturamento", "Lucro Líquido"]], use_container_width=True)
    else:
        st.info("Nenhuma venda registrada neste período.")

elif menu == "Cadastrar / Listar Produtos":
    exibir_headline("Gerenciamento de Produtos", "Cadastre novos itens salvos diretamente na nuvem.")
    
    with st.expander("➕ Expandir Formulário para Novo Produto", expanded=True):
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
                novo_produto = {
                    "sku": sku, "produto": nome, "custo": custo, 
                    "preco_venda": preco_venda, "taxa_ml": taxa_ml, 
                    "frete_medio": frete_medio, "estoque": estoque
                }
                try:
                    supabase.table("produtos").insert(novo_produto).execute()
                    st.success(f"Produto '{nome}' salvo no banco de dados!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar produto: {e}")

    st.subheader("Catálogo de Produtos")
    if not df_produtos.empty:
        st.dataframe(df_produtos, use_container_width=True)
        
        with st.expander("🗑️ Excluir Produto por SKU"):
            sku_para_excluir = st.selectbox("Selecione o SKU para remover", df_produtos["sku"].tolist())
            if st.button("Excluir Produto Permanentemente"):
                try:
                    supabase.table("produtos").delete().eq("sku", sku_para_excluir).execute()
                    st.success("Produto excluído com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")
    else:
        st.info("Nenhum produto cadastrado.")

elif menu == "Registrar Venda":
    exibir_headline("Registrar Nova Venda", "Lançamentos salvos permanentemente na nuvem.")
    
    if df_produtos.empty:
        st.warning("Cadastre produtos primeiro na aba de Gerenciamento.")
    else:
        with st.expander("🛒 Nova Venda", expanded=True):
            with st.form("form_venda"):
                col1, col2 = st.columns(2)
                with col1:
                    prod_vendido = st.selectbox("Escolha o Produto", df_produtos["produto"].tolist())
                    qtd_vendida = st.number_input("Quantidade Vendida", min_value=1, value=1, step=1)
                with col2:
                    data_venda = st.date_input("Data da Venda", datetime.now())
                    forma_pgto = st.selectbox("Forma de Pagamento", ["Mercado Livre", "PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Outro"])
                
                if st.form_submit_button("Confirmar e Registrar Venda"):
                    p_info = df_produtos[df_produtos["produto"] == prod_vendido].iloc[0]
                    
                    nova_venda = {
                        "data": datetime.combine(data_venda, datetime.min.time()).isoformat(),
                        "sku": p_info["sku"],
                        "produto": prod_vendido,
                        "qtd": int(qtd_vendida),
                        "pagamento": forma_pgto,
                        "preco_unit": float(p_info["preco_venda"]),
                        "custo_unit": float(p_info["custo"]),
                        "taxa_ml": float(p_info["preco_venda"] * (p_info["taxa_ml"] / 100)) if forma_pgto == "Mercado Livre" else 0.0,
                        "frete": float(p_info["frete_medio"]) if forma_pgto == "Mercado Livre" else 0.0
                    }
                    
                    try:
                        supabase.table("vendas").insert(nova_venda).execute()
                        novo_estoque = int(p_info["estoque"]) - int(qtd_vendida)
                        supabase.table("produtos").update({"estoque": novo_estoque}).eq("sku", p_info["sku"]).execute()
                        st.success("Venda registrada e estoque atualizado na nuvem!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar venda: {e}")

    st.subheader("Histórico Geral de Vendas")
    if not df_vendas.empty:
        st.dataframe(df_vendas[["id", "data", "produto", "qtd", "pagamento", "preco_unit"]], use_container_width=True)
        
        with st.expander("🗑️ Excluir Venda por ID"):
            id_para_excluir = st.number_input("Digite o ID da venda que deseja apagar", min_value=1, step=1)
            if st.button("Excluir Venda"):
                try:
                    supabase.table("vendas").delete().eq("id", id_para_excluir).execute()
                    st.success("Venda removida do histórico!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir: {e}")
    else:
        st.info("O histórico de vendas está vazio.")

elif menu == "Simulador de Lucro por Venda":
    exibir_headline("Simulador de Lucro Real", "Análise detalhada descontando comissões do marketplace, frete e custos.")
    
    if df_produtos.empty:
        st.warning("Cadastre produtos primeiro.")
    else:
        produto_selecionado = st.selectbox("Selecione o Produto", df_produtos["produto"].tolist())
        prod_data = df_produtos[df_produtos["produto"] == produto_selecionado].iloc[0]
        
        preco = float(prod_data["preco_venda"])
        custo = float(prod_data["custo"])
        taxa_ml_pct = float(prod_data["taxa_ml"]) / 100
        frete = float(prod_data["frete_medio"])
        
        valor_taxa_ml = preco * taxa_ml_pct
        lucro_bruto = preco - custo - valor_taxa_ml - frete
        margem_lucro = (lucro_bruto / preco * 100) if preco > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço de Venda", formatar_moeda(preco))
        col2.metric("Custo de Aquisição", formatar_moeda(custo))
        col3.metric("Taxa ML + Frete", formatar_moeda(valor_taxa_ml + frete))
        col4.metric("Lucro Líquido Real", formatar_moeda(lucro_bruto), f"{margem_lucro:.1f}%")
        
        if margem_lucro < 10:
            st.error("⚠️ Atenção: Sua margem de lucro está abaixo de 10%!")
        elif margem_lucro >= 20:
            st.success("✅ Margem de lucro saudável e dentro do planejado!")

elif menu == "Controle de Estoque":
    exibir_headline("Gestão de Estoque", "Acompanhe o saldo físico dos produtos na nuvem.")
    if not df_produtos.empty:
        st.dataframe(df_produtos[["sku", "produto", "estoque"]], use_container_width=True)
        baixo_estoque = df_produtos[df_produtos["estoque"] <= 3]
        if not baixo_estoque.empty:
            st.warning("⚠️ Alerta: Produtos com estoque crítico:")
            st.table(baixo_estoque[["sku", "produto", "estoque"]])
    else:
        st.info("Estoque vazio.")