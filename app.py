import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# ==============================
# ⚙️ CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(page_title="Controle de Chaves", layout="wide")

# ======== ESTILO VISUAL ========
st.markdown("""
<style>
/* ===== TEMA GERAL ===== */
body {background-color: #0f1a3d; color: #ffffff;}
.stApp {background-color: #0f1a3d;}
h1, h2, h3, h4, label, p, span, div, input, button, textarea {color: #ffffff !important;}

/* ===== ÍCONES (emojis pretos) ===== */
h1 span, h2 span, h3 span, h4 span {
    color: #000000 !important;
}

/* ===== BOTÕES ===== */
div[data-testid="stHorizontalBlock"] button,
.stButton>button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 8px !important;
    padding: 0.6em 1.3em !important;
    font-size: 1.05em !important;
    font-weight: 600 !important;
    margin-right: 10px !important;
    transition: 0.3s ease-in-out;
}
div[data-testid="stHorizontalBlock"] button:hover,
.stButton>button:hover {
    background-color: #1e3a8a !important;
    color: #ffffff !important;
    border: 1px solid #3a5acb !important;
}

/* ===== INPUTS ===== */
.stTextInput>div>div>input {
    background-color: #1c2750 !important;
    color: #ffffff !important;
    border: 1px solid #3a4a7c !important;
    border-radius: 6px !important;
}

/* ===== TABELAS ===== */
[data-testid="stDataFrame"] {
    background-color: #16224d !important;
    border-radius: 6px !important;
    border: 1px solid #2b3b70 !important;
    padding: 10px;
}

/* ===== ALERTAS ===== */
.stAlert {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ======== TÍTULO ========
st.markdown("<h1><span style='color:black;'>🔑</span> Sistema Corporativo de Controle de Chaves</h1>", unsafe_allow_html=True)

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
# 🧭 MENU SUPERIOR
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
    st.markdown("<h3><span style='color:black;'>➕</span> Registrar Novo Empréstimo de Chave</h3>", unsafe_allow_html=True)
    chave = st.text_input("Número da Chave:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("💾 Registrar Empréstimo"):
        if chave and usuario:
            registrar_emprestimo(chave, usuario)
            st.success(f"✅ Empréstimo registrado: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de salvar.")

elif st.session_state.pagina == "devolucao":
    st.markdown("<h3><span style='color:black;'>🔁</span> Registrar Devolução de Chave</h3>", unsafe_allow_html=True)
    chave = st.text_input("Número da Chave para Devolução:")
    usuario = st.text_input("Usuário / Chapa:")
    if st.button("📦 Confirmar Devolução"):
        if chave and usuario:
            registrar_devolucao(chave, usuario)
            st.success(f"🔙 Devolução registrada: Chave {chave} - Usuário {usuario}")
        else:
            st.warning("⚠️ Preencha todos os campos antes de confirmar.")

elif st.session_state.pagina == "historico":
    st.markdown("<h3><span style='color:black;'>🕓</span> Histórico de Movimentações</h3>", unsafe_allow_html=True)

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
    else:
        st.info("Histórico está oculto no momento.")

    st.markdown("---")
    st.write("🧹 **Gerenciar histórico exibido na tela (sem alterar o banco ou relatórios):**")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧼 Limpar Histórico da Tela"):
            st.session_state.mostrar_historico = False
            st.info("Histórico ocultado da tela. Dados e relatórios permanecem salvos.")
    with col_b:
        if st.button("👁 Mostrar Histórico Novamente"):
            st.session_state.mostrar_historico = True
            st.success("Histórico restaurado na tela com sucesso!")

# ==============================
# 📊 SITUAÇÃO ATUAL
# ==============================
st.markdown("---")
st.markdown("<h3><span style='color:black;'>📋</span> Situação Atual das Chaves</h3>", unsafe_allow_html=True)

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
# Forçando atualização - versão corrigida com ícones pretos e títulos em markdown
