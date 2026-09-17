import streamlit as st
import requests
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(
    page_title="ERP Bmakeup",
    page_icon="💄",
    layout="wide"
)

# Inicialização do Supabase usando o st.secrets (Cofre seguro)
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_supabase()

# Sistema de Login Simples
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_login():
    if not st.session_state["authenticated"]:
        st.title("🔒 Login - ERP Bmakeup")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if username == "admin" and password == "bmstore2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        return False
    return True

if not check_login():
    st.stop()

# Menu Lateral
st.sidebar.image("logo.png", width=150) if "logo.png" in locals() else None
st.sidebar.title("Menu Principal")
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Produtos", "Vendas", "🔌 Integração Mercado Livre"])

# -------------------------------------------------------------
# ABA: PAINEL GERAL
# -------------------------------------------------------------
if menu == "Painel Geral":
    st.title("📊 Painel Geral - Bmakeup")
    st.info("Bem-vindo ao seu ERP otimizado e seguro!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Produtos Cadastrados", "---")
    col2.metric("Vendas Hoje", "R$ 0,00")
    col3.metric("Status da Integração ML", "Verificando...")

# -------------------------------------------------------------
# ABA: PRODUTOS
# -------------------------------------------------------------
elif menu == "Produtos":
    st.title("📦 Gestão de Produtos")
    st.write("Aqui você visualiza e gerencia o estoque do seu ERP.")

# -------------------------------------------------------------
# ABA: VENDAS
# -------------------------------------------------------------
elif menu == "Vendas":
    st.title("🛒 Histórico de Vendas")
    st.write("Acompanhe as vendas realizadas.")

# -------------------------------------------------------------
# ABA: INTEGRAÇÃO MERCADO LIVRE
# -------------------------------------------------------------
elif menu == "🔌 Integração Mercado Livre":
    st.title("Integração Oficial - Mercado Livre")
    
    # Pega as chaves do cofre do Streamlit
    try:
        ML_APP_ID = st.secrets["ML_APP_ID"]
        ML_CLIENT_SECRET = st.secrets["ML_CLIENT_SECRET"]
        ML_REDIRECT_URI = st.secrets["ML_REDIRECT_URI"]
    except Exception as e:
        st.error(f"Erro ao carregar as chaves do Mercado Livre no st.secrets: {e}")
        st.stop()

    # Verifica se já existe um token salvo no Supabase
    try:
        response = supabase.table("ml_tokens").select("*").execute()
        tokens_data = response.data
    except Exception:
        tokens_data = []

    is_connected = len(tokens_data) > 0

    if is_connected:
        st.success("🟢 STATUS: Conectado ao Mercado Livre com Sucesso!")
        st.write("Seu ERP está pronto para sincronizar dados e ler o catálogo com total segurança.")
        if st.button("Desconectar Conta"):
            supabase.table("ml_tokens").delete().neq("id", 0).execute()
            st.rerun()
    else:
        st.warning("🟡 STATUS: Desconectado. Nenhuma credencial encontrada.")
        st.write("Para iniciar, clique no botão abaixo. Você será levado ao Mercado Livre para aprovar a permissão de leitura, e retornará automaticamente para o seu ERP.")

        # URL de Autenticação Blindada e Corrigida com https://
        ml_auth_url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={ML_APP_ID}&redirect_uri={ML_REDIRECT_URI}"

        st.markdown(f"""
            <br>
            <a href="{ml_auth_url}" target="_self">
                <button style="background-color:#ffe600; color:#2d3277; padding:12px 24px; border:none; border-radius:5px; font-weight:bold; font-size:16px; cursor:pointer;">
                    Conectar Conta do Mercado Livre
                </button>
            </a>
            <br><br>
        """, unsafe_allow_html=True)

    # Captura o código de retorno enviado pelo Mercado Livre após a autorização
    query_params = st.query_params
    if "code" in query_params:
        auth_code = query_params["code"]
        
        # Troca o código temporário pelo Access Token definitivo
        token_url = "https://api.mercadolibre.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": ML_APP_ID,
            "client_secret": ML_CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": ML_REDIRECT_URI
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(token_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_json = response.json()
            access_token = token_json.get("access_token")
            refresh_token = token_json.get("refresh_token")
            
            # Salva os tokens de forma segura no Supabase
            supabase.table("ml_tokens").insert({
                "access_token": access_token,
                "refresh_token": refresh_token
            }).execute()
            
            st.success("Conta conectada e tokens salvos com sucesso!")
            st.query_params.clear()
            st.rerun()
        else:
            st.error(f"Erro ao autenticar com o Mercado Livre: {response.text}")
