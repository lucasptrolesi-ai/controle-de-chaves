import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==============================
# ⚙️ CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(page_title="Controle de Chaves", layout="wide")

st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
.stApp {background-color: #0e1117;}
h1, h2, h3, h4 {text-align: center; color: #00ADB5;}
/* Botões da navbar */
div[data-testid="stHorizontalBlock"] button {
    background-color: #00ADB5 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6em 1.3em !important;
    font-size: 1.05em !important;
    font-weight: 600 !important;
    margin-right: 10px !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background-color: #06c3cc !important;
    color: black !important;
}
.stTextInput>div>div>input {
    background-color: #222831 !important;
    color: white !important;
    border: 1px solid #393E46 !important;
    border-radius: 6px !important;
}
.dataframe {
    background-color: #222831 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🔑 Sistema Corporativo de Controle de Chaves</h1>", unsafe_allow_html=True)

# ==============================
# 🔗 BANCO DE DADOS (SQLite)
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
# 💾 FUNÇÕES
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
    return pd.read_sql("SELECT chave AS 'Chave', usuario AS 'Usuário/Chapa', status AS 'Status', data AS 'Data' FROM chaves", conn)

def carregar_historico():
    return pd.read_sql("SELECT chave AS 'Chave', usuario AS 'Usuário/Chapa', acao AS 'Ação', status AS 'Status', data AS 'Data' FROM historico", conn)

# ==============================
# 🧭 MENU SUPERIOR FIXO (NAVBAR)
# ==============================
st.markdown("---")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    menu = st.button("➕ Novo Empréstimo")
with col2:
    menu2 = st.button("🔁 Registrar Devolução")
with col3:
    menu3 = st.button("🕓 Histórico")
with col4:
    menu4 = st.button("🧹 Limpar Campos")
st.markdown("---")

# 🔄 Mantém o estado ativo do menu (para evitar sumir ao digitar)
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if menu:
    st.session_state.pagina = "emprestimo"
elif menu2:
    st.session_state.pagina = "devolucao"
elif menu3:
    st.session_state.pagina = "historico"
elif menu4:
    st.session_state.pagina = "inicio"

# ==============================
# 📋 PÁGINAS FUNCIONAIS
# ==============================
if st.session_state.pagina == "emprestimo":
    st.subheader("➕ Registrar Novo Empréstimo de Chave")
    chave = st.text_input("Número da Chave:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("💾 Registrar Empréstimo"):
        if chave and usuario:
            registrar_emprestimo(chave, usuario)
            st.success(f"✅ Empréstimo registrado: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de salvar.")

elif st.session_state.pagina == "devolucao":
    st.subheader("🔁 Registrar Devolução de Chave")
    chave = st.text_input("Número da Chave para Devolução:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("📦 Confirmar Devolução"):
        if chave and usuario:
            registrar_devolucao(chave, usuario)
            st.success(f"🔙 Devolução registrada: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de confirmar.")

elif st.session_state.pagina == "historico":
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

# ==============================
# 📊 SITUAÇÃO ATUAL (FIXA)
# ==============================
import io

# ==============================
# 📊 SITUAÇÃO ATUAL (FIXA)
# ==============================
st.markdown("---")
st.subheader("📋 Situação Atual das Chaves")

df = carregar_chaves()
if df.empty:
    st.info("Nenhum registro encontrado ainda.")
else:
    st.dataframe(df, use_container_width=True)

    # ✅ Corrigido: gerar Excel em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Chaves")

    st.download_button(
        label="⬇️ Baixar Planilha Excel",
        data=buffer.getvalue(),
        file_name="controle_chaves.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==============================
# 📍 RODAPÉ
# ==============================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 - Sistema Corporativo de Controle de Chaves | Desenvolvido por Lucas Trolesi</p>",
    unsafe_allow_html=True
)
