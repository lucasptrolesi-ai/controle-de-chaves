# ===========================================
# 🔑 SISTEMA DE CONTROLE DE CHAVES ONLINE 3.3
# ===========================================
# ✅ Compatível com Streamlit Cloud e VS Code
# ✅ Cria arquivos Excel automaticamente
# ✅ Empréstimos, devoluções e duplicadas
# ✅ Histórico automático e filtros
# ===========================================

import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

# ==============================
# ⚙️ Configuração da página
# ==============================
st.set_page_config(page_title="Controle de Chaves", page_icon="🔑", layout="wide")

# ==============================
# 📂 Arquivos
# ==============================
ARQUIVO_DADOS = "controle_chaves.xlsx"
ARQUIVO_HISTORICO = "historico_movimentacoes.xlsx"

# Cria arquivos vazios se não existirem
if not os.path.exists(ARQUIVO_DADOS):
    pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Status", "Data"]).to_excel(ARQUIVO_DADOS, index=False)

if not os.path.exists(ARQUIVO_HISTORICO):
    pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Ação", "Status", "Data"]).to_excel(ARQUIVO_HISTORICO, index=False)

# ==============================
# 🧩 Funções auxiliares
# ==============================
def carregar_dados(caminho):
    df = pd.read_excel(caminho)
    df.columns = [col.strip().title() for col in df.columns]
    return df

def salvar_dados(df, caminho):
    df.to_excel(caminho, index=False)

def registrar_movimentacao(chave, usuario, acao, status):
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nova = pd.DataFrame([{
        "Chave": chave,
        "Usuário/Chapa": usuario,
        "Ação": acao,
        "Status": status,
        "Data": data
    }])
    hist = pd.read_excel(ARQUIVO_HISTORICO)
    hist = pd.concat([hist, nova], ignore_index=True)
    salvar_dados(hist, ARQUIVO_HISTORICO)

# ==============================
# 📥 Carregar base inicial
# ==============================
df = carregar_dados(ARQUIVO_DADOS)

# ==============================
# 🎨 Cabeçalho
# ==============================
st.title("🔑 Sistema de Controle de Chaves")
st.markdown("Gerencie **empréstimos, devoluções e duplicadas** com histórico automático e gráficos em tempo real.")

# ==============================
# 📤 Atualizar base manualmente
# ==============================
st.sidebar.header("📂 Atualizar Banco de Dados")
arquivo_upload = st.sidebar.file_uploader("Envie o arquivo controle_chaves.xlsx", type=["xlsx"])
if arquivo_upload is not None:
    df = pd.read_excel(arquivo_upload)
    salvar_dados(df, ARQUIVO_DADOS)
    st.sidebar.success("✅ Base de dados atualizada com sucesso!")

# ==============================
# 📊 Resumo e gráfico
# ==============================
st.subheader("📊 Situação Atual das Chaves")

total = len(df)
emprestadas = (df["Status"] == "Empréstimo").sum()
devolvidas = (df["Status"] == "Devolvido").sum()
duplicadas = (df["Status"] == "Duplicada").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔹 Total", total)
col2.metric("🔸 Empréstimos", emprestadas)
col3.metric("🟢 Devolvidas", devolvidas)
col4.metric("⚠️ Duplicadas", duplicadas)

# === Gráfico Matplotlib ===
st.markdown("### 📈 Gráfico de Status das Chaves")
fig, ax = plt.subplots()
ax.bar(["Empréstimo", "Devolvido", "Duplicada"], [emprestadas, devolvidas, duplicadas],
       color=["#FFD966", "#93C47D", "#EA9999"])
ax.set_ylabel("Quantidade")
ax.set_title("Distribuição de Status das Chaves")
st.pyplot(fig)

# ==============================
# 🔍 Filtros e tabela
# ==============================
st.markdown("### 🔍 Filtros e Visualização")

status_filtro = st.selectbox("Filtrar por status:", ["Todos"] + sorted(df["Status"].dropna().unique().tolist()))
usuario_filtro = st.selectbox("Filtrar por usuário/chapa:", ["Todos"] + sorted(df["Usuário/Chapa"].dropna().unique().tolist()))

df_filtrado = df.copy()
if status_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtro]
if usuario_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Usuário/Chapa"] == usuario_filtro]

def colorir_status(valor):
    if valor == "Empréstimo":
        return "background-color: #FFF2CC;"
    elif valor == "Devolvido":
        return "background-color: #C6E0B4;"
    elif valor == "Duplicada":
        return "background-color: #F4CCCC;"
    else:
        return ""

st.dataframe(df_filtrado.style.applymap(colorir_status, subset=["Status"]), use_container_width=True)

# ==============================
# 🔘 Botões principais
# ==============================
st.markdown("---")
col1, col2 = st.columns(2)
abrir_novo = col1.button("➕ Novo Empréstimo")
abrir_dev = col2.button("↩️ Registrar Devolução")

# =====================================================
# ➕ Novo Empréstimo
# =====================================================
if abrir_novo:
    st.subheader("➕ Registrar Novo Empréstimo")
    with st.form("form_emprestimo"):
        usuario = st.text_input("Usuário/Chapa:")
        chaves_input = st.text_area("Chaves (separe por vírgula):", placeholder="Exemplo: 101, 102, 103")
        enviar = st.form_submit_button("Salvar")

    if enviar:
        if not usuario or not chaves_input:
            st.warning("⚠️ Preencha todos os campos.")
        else:
            chaves = [c.strip() for c in chaves_input.split(",")]
            duplicadas = []
            for chave in chaves:
                duplicada = (df["Chave"] == chave) & (df["Status"] == "Empréstimo")
                if duplicada.any():
                    duplicadas.append(chave)
                    status = "Duplicada"
                else:
                    status = "Empréstimo"

                nova = pd.DataFrame([{
                    "Chave": chave,
                    "Usuário/Chapa": usuario,
                    "Status": status,
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }])
                df = pd.concat([df, nova], ignore_index=True)
                registrar_movimentacao(chave, usuario, "Empréstimo", status)

            salvar_dados(df, ARQUIVO_DADOS)
            if duplicadas:
                st.error(f"❌ Já emprestadas: {', '.join(duplicadas)}")
            st.success(f"✅ Empréstimo registrado para {usuario}!")

# =====================================================
# ↩️ Devolução
# =====================================================
if abrir_dev:
    st.subheader("↩️ Registrar Devolução")
    usuarios = sorted(df["Usuário/Chapa"].dropna().unique().tolist())
    if usuarios:
        usuario_sel = st.selectbox("Selecione o usuário:", usuarios)
        chaves_usuario = df[(df["Usuário/Chapa"] == usuario_sel) & (df["Status"] == "Empréstimo")]["Chave"].tolist()

        if chaves_usuario:
            st.write(f"🔑 Empréstimos de **{usuario_sel}**: {', '.join(chaves_usuario)}")

            col1, col2 = st.columns(2)
            if col1.button("Devolução Total"):
                df.loc[(df["Usuário/Chapa"] == usuario_sel) & (df["Status"] == "Empréstimo"), "Status"] = "Devolvido"
                salvar_dados(df, ARQUIVO_DADOS)
                for chave in chaves_usuario:
                    registrar_movimentacao(chave, usuario_sel, "Devolução Total", "Devolvido")
                st.success(f"✅ Todas as chaves de {usuario_sel} foram devolvidas.")

            chaves_parciais = col2.multiselect("Selecione para devolução parcial:", chaves_usuario)
            if st.button("Confirmar Devolução Parcial"):
                for chave in chaves_parciais:
                    df.loc[(df["Chave"] == chave) & (df["Status"] == "Empréstimo"), "Status"] = "Devolvido"
                    registrar_movimentacao(chave, usuario_sel, "Devolução Parcial", "Devolvido")
                salvar_dados(df, ARQUIVO_DADOS)
                st.success("✅ Devolução parcial concluída!")
        else:
            st.info("📭 Nenhuma chave emprestada por esse usuário.")
    else:
        st.info("📂 Nenhum usuário encontrado.")

# =====================================================
# 🕓 Histórico
# =====================================================
st.markdown("---")
st.subheader("🕓 Histórico de Movimentações")
hist = pd.read_excel(ARQUIVO_HISTORICO)
st.dataframe(hist, use_container_width=True)
st.download_button("⬇️ Baixar histórico (CSV)", hist.to_csv(index=False).encode("utf-8"), "historico_chaves.csv")
