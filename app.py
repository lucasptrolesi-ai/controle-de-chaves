import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==============================
# ⚙️ Configuração da página
# ==============================
st.set_page_config(page_title="Controle de Chaves", layout="wide")
st.title("🔑 Sistema de Controle de Chaves")

# ==============================
# 🔗 Conexão com o banco SQLite
# ==============================
conn = sqlite3.connect("controle_chaves.db", check_same_thread=False)
cursor = conn.cursor()

# Criação das tabelas, se não existirem
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
# 🎨 Interface do sistema
# ==============================
aba = st.sidebar.radio("Menu", ["📋 Ver Chaves", "➕ Novo Empréstimo", "🔁 Registrar Devolução", "🕓 Histórico"])

if aba == "📋 Ver Chaves":
    st.subheader("📋 Situação Atual das Chaves")
    df = carregar_chaves()
    if df.empty:
        st.info("Nenhum registro encontrado ainda.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Baixar Excel", df.to_excel(index=False).encode("utf-8"), "controle_chaves.xlsx")

elif aba == "➕ Novo Empréstimo":
    st.subheader("➕ Registrar Novo Empréstimo")
    chave = st.text_input("Número da Chave:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("Registrar Empréstimo"):
        if chave and usuario:
            registrar_emprestimo(chave, usuario)
            st.success(f"✅ Empréstimo registrado: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos.")

elif aba == "🔁 Registrar Devolução":
    st.subheader("🔁 Registrar Devolução de Chave")
    chave = st.text_input("Número da Chave para Devolução:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("Confirmar Devolução"):
        if chave and usuario:
            registrar_devolucao(chave, usuario)
            st.success(f"🔙 Devolução registrada: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos.")

elif aba == "🕓 Histórico":
    st.subheader("🕓 Histórico de Movimentações")
    df_hist = carregar_historico()
    if df_hist.empty:
        st.info("Nenhuma movimentação registrada.")
    else:
        st.dataframe(df_hist, use_container_width=True)
        st.download_button("⬇️ Exportar Histórico (CSV)", df_hist.to_csv(index=False).encode("utf-8"), "historico_movimentacoes.csv")

st.sidebar.markdown("---")
st.sidebar.info("💾 Os dados são armazenados localmente em **SQLite (controle_chaves.db)** e mantidos mesmo após fechar o app.")
