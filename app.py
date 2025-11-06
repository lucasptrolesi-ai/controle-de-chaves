import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==============================
# ⚙️ Configuração da página
# ==============================
st.set_page_config(page_title="Controle de Chaves", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    h1, h2, h3 {
        text-align: center;
        color: #00ADB5;
        font-weight: 600;
    }
    .css-1d391kg, .stButton>button {
        background-color: #00ADB5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6em 1.2em !important;
        font-size: 1em !important;
        font-weight: 600 !important;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #06c3cc !important;
        color: black !important;
    }
    .stTextInput>div>div>input {
        background-color: #222831 !important;
        color: white !important;
        border: 1px solid #393E46 !important;
        border-radius: 5px !important;
    }
    .stDataFrame {
        background-color: #222831 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1>🔑 Sistema Corporativo de Controle de Chaves</h1>", unsafe_allow_html=True)

# ==============================
# 🔗 Conexão com o banco SQLite
# ==============================
conn = sqlite3.connect("controle_chaves.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT,
    usuario TEXT,
    status TEXT,
    data TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT,
    usuario TEXT,
    acao TEXT,
    status TEXT,
    data TEXT
)
""")

conn.commit()

# ==============================
# 💾 Funções de manipulação
# ==============================
def registrar_emprestimo(chave, usuario):
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("INSERT INTO chaves (chave, usuario, status, data) VALUES (?, ?, ?, ?)",
                   (chave, usuario, "Emprestado", data))
    cursor.execute("INSERT INTO historico (chave, usuario, acao, status, data) VALUES (?, ?, ?, ?, ?)",
                   (chave, usuario, "Empréstimo", "Emprestado", data))
    conn.commit()

def registrar_devolucao(chave, usuario):
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("UPDATE chaves SET status = 'Devolvido' WHERE chave = ?", (chave,))
    cursor.execute("INSERT INTO historico (chave, usuario, acao, status, data) VALUES (?, ?, ?, ?, ?)",
                   (chave, usuario, "Devolução", "Devolvido", data))
    conn.commit()

def carregar_chaves():
    return pd.read_sql("SELECT chave, usuario, status, data FROM chaves", conn)

def carregar_historico():
    return pd.read_sql("SELECT chave, usuario, acao, status, data FROM historico", conn)

# ==============================
# 🎨 Interface Corporativa
# ==============================
menu = st.sidebar.radio(
    "Menu Principal",
    ["📋 Ver Chaves", "➕ Novo Empréstimo", "🔁 Registrar Devolução", "🕓 Histórico"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🌐 Modo: Corporativo | Tema Escuro**")
st.sidebar.markdown("💾 Banco de Dados: `controle_chaves.db`")

if menu == "📋 Ver Chaves":
    st.subheader("📋 Situação Atual das Chaves")
    df = carregar_chaves()
    if df.empty:
        st.info("Nenhum registro encontrado ainda.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇️ Baixar Planilha Excel",
            df.to_excel(index=False).encode("utf-8"),
            "controle_chaves.xlsx"
        )

elif menu == "➕ Novo Empréstimo":
    st.subheader("➕ Registrar Novo Empréstimo de Chave")
    col1, col2 = st.columns(2)
    with col1:
        chave = st.text_input("Número da Chave:")
    with col2:
        usuario = st.text_input("Usuário / Chapa:")
    if st.button("💾 Registrar Empréstimo"):
        if chave and usuario:
            registrar_emprestimo(chave, usuario)
            st.success(f"✅ Empréstimo registrado: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de salvar.")

elif menu == "🔁 Registrar Devolução":
    st.subheader("🔁 Registrar Devolução de Chave")
    col1, col2 = st.columns(2)
    with col1:
        chave = st.text_input("Número da Chave para Devolução:")
    with col2:
        usuario = st.text_input("Usuário / Chapa:")
    if st.button("📦 Confirmar Devolução"):
        if chave and usuario:
            registrar_devolucao(chave, usuario)
            st.success(f"🔙 Devolução registrada: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de confirmar.")

elif menu == "🕓 Histórico":
    st.subheader("🕓 Histórico de Movimentações")
    df_hist = carregar_historico()
    if df_hist.empty:
        st.info("Nenhuma movimentação registrada ainda.")
    else:
        st.dataframe(df_hist, use_container_width=True)
        st.download_button(
            "⬇️ Exportar Histórico CSV",
            df_hist.to_csv(index=False).encode("utf-8"),
            "historico_movimentacoes.csv"
        )
