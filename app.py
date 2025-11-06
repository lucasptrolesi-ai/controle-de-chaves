# ===========================================
# 🔑 SISTEMA DE CONTROLE DE CHAVES ONLINE 3.2
# ===========================================
# ✅ Cria arquivos automaticamente se não existirem
# ✅ Lê e grava base Excel
# ✅ Registro de empréstimos e devoluções
# ✅ Histórico automático
# ✅ Funciona sem base inicial
# ===========================================

import streamlit as st
import pandas as pd
from datetime import datetime
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

# ✅ Cria automaticamente os arquivos, se não existirem
if not os.path.exists(ARQUIVO_DADOS):
    df_vazio = pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Status", "Data"])
    df_vazio.to_excel(ARQUIVO_DADOS, index=False)

if not os.path.exists(ARQUIVO_HISTORICO):
    hist_vazio = pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Ação", "Status", "Data"])
    hist_vazio.to_excel(ARQUIVO_HISTORICO, index=False)

# ==============================
# 🧩 Funções auxiliares
# ==============================
def carregar_dados(caminho):
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
    else:
        df = pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Status", "Data"])
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
    if os.path.exists(ARQUIVO_HISTORICO):
        hist = pd.read_excel(ARQUIVO_HISTORICO)
        hist = pd.concat([hist, nova], ignore_index=True)
    else:
        hist = nova
    hist.to_excel(ARQUIVO_HISTORICO, index=False)

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
st.sidebar.header("📁 Atualizar Banco de Dados")
arquivo_upload = st.sidebar.file_uploader("Envie o arquivo controle_chaves.xlsx", type=["xlsx"])
if arquivo_upload is not None:
    df = pd.read_excel(arquivo_upload)
    st.sidebar.success("✅ Base de dados atualizada com sucesso!")
    salvar_dados(df, ARQUIVO_DADOS)

# ==============================
# 📊 Visão Geral
# ==============================
st.subheader("🔍 Filtros e Visualização")

col1, col2 = st.columns(2)
with col1:
    status_filtro = st.selectbox("Filtrar por status:", ["Todos"] + sorted(df["Status"].dropna().unique().tolist()))
with col2:
    usuario_filtro = st.selectbox("Filtrar por usuário/chapa:", ["Todos"] + sorted(df["Usuário/Chapa"].dropna().unique().tolist()))

df_filtrado = df.copy()
if status_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtro]
if usuario_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Usuário/Chapa"] == usuario_filtro]

st.dataframe(df_filtrado, use_container_width=True)

# ==============================
# 🔘 BOTÕES DE AÇÃO
# ==============================
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    abrir_novo = st.button("➕ Novo Empréstimo")
with col2:
    abrir_devolucao = st.button("↩️ Registrar Devolução")

# =====================================================
# 🔹 NOVO EMPRÉSTIMO
# =====================================================
if abrir_novo:
    with st.form("form_emprestimo"):
        usuario = st.text_input("Usuário/Chapa:")
        chaves_input = st.text_area("Digite as chaves (separe por vírgula):", placeholder="Exemplo: 101, 102, 105")
        enviar = st.form_submit_button("Salvar Empréstimos")

    if enviar:
        if not usuario or not chaves_input:
            st.warning("⚠️ Preencha todos os campos.")
        else:
            chaves = [c.strip() for c in chaves_input.split(",") if c.strip()]
            duplicadas = []
            for chave in chaves:
                duplicada = (df["Chave"] == chave) & (df["Status"] == "Empréstimo")
                if duplicada.any():
                    duplicadas.append(chave)
                    nova = pd.DataFrame([{
                        "Chave": chave,
                        "Usuário/Chapa": usuario,
                        "Status": "Duplicada",
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }])
                    df = pd.concat([df, nova], ignore_index=True)
                    registrar_movimentacao(chave, usuario, "Tentativa de Empréstimo", "Duplicada")
                else:
                    nova = pd.DataFrame([{
                        "Chave": chave,
                        "Usuário/Chapa": usuario,
                        "Status": "Empréstimo",
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }])
                    df = pd.concat([df, nova], ignore_index=True)
                    registrar_movimentacao(chave, usuario, "Empréstimo", "Empréstimo")

            salvar_dados(df, ARQUIVO_DADOS)
            if duplicadas:
                st.error(f"❌ As seguintes chaves já estavam emprestadas: {', '.join(duplicadas)}")
            st.success(f"✅ Empréstimo registrado com sucesso para {usuario}!")

# =====================================================
# 🔹 DEVOLUÇÃO DE CHAVES
# =====================================================
if abrir_devolucao:
    usuarios = sorted(df["Usuário/Chapa"].dropna().unique().tolist())
    if usuarios:
        usuario_sel = st.selectbox("Selecione o usuário/chapa:", usuarios)
        chaves_usuario = df[(df["Usuário/Chapa"] == usuario_sel) & (df["Status"] == "Empréstimo")]["Chave"].tolist()

        if chaves_usuario:
            st.write(f"🔑 Chaves emprestadas por **{usuario_sel}**: {', '.join(map(str, chaves_usuario))}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Devolução Total"):
                    df.loc[(df["Usuário/Chapa"] == usuario_sel) & (df["Status"] == "Empréstimo"), "Status"] = "Devolvido"
                    salvar_dados(df, ARQUIVO_DADOS)
                    for chave in chaves_usuario:
                        registrar_movimentacao(chave, usuario_sel, "Devolução Total", "Devolvido")
                    st.success(f"✅ Todas as chaves de {usuario_sel} foram devolvidas.")
            with col2:
                chaves_parciais = st.multiselect("Selecione as chaves a devolver (parcial):", chaves_usuario)
                if st.button("Confirmar Devolução Parcial"):
                    if chaves_parciais:
                        for chave in chaves_parciais:
                            df.loc[(df["Chave"] == chave) & (df["Status"] == "Empréstimo"), "Status"] = "Devolvido"
                            registrar_movimentacao(chave, usuario_sel, "Devolução Parcial", "Devolvido")
                        salvar_dados(df, ARQUIVO_DADOS)
                        st.success(f"✅ Chaves {', '.join(chaves_parciais)} devolvidas com sucesso.")
                    else:
                        st.warning("Selecione pelo menos uma chave.")
        else:
            st.info("📭 Este usuário não possui chaves emprestadas.")
    else:
        st.info("📂 Nenhum usuário encontrado.")

# =====================================================
# 🔹 HISTÓRICO
# =====================================================
st.markdown("---")
st.subheader("🕓 Histórico de Movimentações")
if os.path.exists(ARQUIVO_HISTORICO):
    hist = pd.read_excel(ARQUIVO_HISTORICO)
    st.dataframe(hist, use_container_width=True)
    st.download_button("⬇️ Baixar histórico (CSV)", hist.to_csv(index=False).encode("utf-8"), "historico_chaves.csv")
else:
    st.info("📭 Nenhum histórico encontrado ainda.")
