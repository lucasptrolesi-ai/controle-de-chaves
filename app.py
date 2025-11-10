import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# ==============================
# ⚙️ CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(page_title="Controle de Chaves", layout="wide")

# Tema azul corporativo
st.markdown("""
<style>
body {background-color: #0f1a3d; color: #ffffff;}
.stApp {background-color: #0f1a3d;}
h1, h2, h3, h4, label, p, span, div, input, button, textarea {color: #ffffff !important;}
/* Navbar */
div[data-testid="stHorizontalBlock"] button {
    background-color: #1e3a8a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6em 1.3em !important;
    font-size: 1.05em !important;
    font-weight: 600 !important;
    margin-right: 10px !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background-color: #2b5fc0 !important;
    color: white !important;
}
/* Inputs */
.stTextInput>div>div>input {
    background-color: #1c2750 !important;
    color: #ffffff !important;
    border: 1px solid #3a4a7c !important;
    border-radius: 6px !important;
}
/* DataFrame */
[data-testid="stDataFrame"] {
    background-color: #16224d !important;
    border-radius: 6px !important;
    border: 1px solid #2b3b70 !important;
    padding: 10px;
}
/* Mensagens */
.stAlert {
    border-radius: 8px !important;
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

    if "mostrar_historico" not in st.session_state:
        st.session_state.mostrar_historico = True

    if st.session_state.mostrar_historico:
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

    st.markdown("---")
    st.write("🧹 **Limpar histórico da tela (sem apagar do banco ou relatórios):**")

    if st.button("🧼 Limpar Histórico da Tela"):
        st.session_state.mostrar_historico = False
        st.info("Histórico ocultado da tela. Dados e relatórios permanecem intactos.")

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
    "<p style='text-align:center; color:#d1d5db;'>© 2025 - Sistema Corporativo de Controle de Chaves | Desenvolvido por Lucas Trolesi</p>",
    unsafe_allow_html=True
)
