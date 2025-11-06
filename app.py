import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ==============================
# 📂 Configuração inicial
# ==============================
st.set_page_config(page_title="Sistema de Controle de Chaves", layout="wide")

ARQUIVO_DADOS = "controle_chaves.xlsx"
ARQUIVO_HISTORICO = "historico_movimentacoes.xlsx"

# Garante que o diretório atual existe
os.makedirs(os.getcwd(), exist_ok=True)

# ==============================
# 💾 Funções auxiliares
# ==============================
def carregar_dados():
    """Carrega ou cria o arquivo principal."""
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_excel(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Status", "Data"])
        df.to_excel(ARQUIVO_DADOS, index=False)
        return df


def carregar_historico():
    """Carrega ou cria o arquivo de histórico."""
    if os.path.exists(ARQUIVO_HISTORICO):
        return pd.read_excel(ARQUIVO_HISTORICO)
    else:
        hist = pd.DataFrame(columns=["Chave", "Usuário/Chapa", "Ação", "Status", "Data"])
        hist.to_excel(ARQUIVO_HISTORICO, index=False)
        return hist


def salvar_dados(df, caminho):
    """Salva DataFrame em Excel com tratamento de erro."""
    try:
        df.to_excel(caminho, index=False)
        st.toast(f"💾 Dados salvos com sucesso: {caminho}")
    except Exception as e:
        st.error(f"⚠️ Erro ao salvar: {e}")


# ==============================
# 📊 Interface principal
# ==============================
st.title("🔑 Sistema de Controle de Chaves")
st.write("Gerencie **empréstimos**, **devoluções** e histórico de movimentações em tempo real.")

dados = carregar_dados()
historico = carregar_historico()

# ==============================
# 🔍 Filtros de visualização
# ==============================
st.subheader("🔎 Filtros e Visualização")

col1, col2 = st.columns(2)
with col1:
    filtro_status = st.selectbox("Filtrar por status:", ["Todos", "Emprestado", "Devolvido"])
with col2:
    filtro_usuario = st.selectbox("Filtrar por usuário/chapa:", ["Todos"] + list(dados["Usuário/Chapa"].unique()))

df_filtrado = dados.copy()
if filtro_status != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Status"] == filtro_status]
if filtro_usuario != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Usuário/Chapa"] == filtro_usuario]

st.dataframe(df_filtrado, width="stretch")

# ==============================
# ➕ Novo Empréstimo
# ==============================
st.markdown("---")
st.subheader("➕ Novo Empréstimo")

with st.form("novo_emprestimo"):
    chave = st.text_input("Número da Chave")
    usuario = st.text_input("Usuário/Chapa")
    enviado = st.form_submit_button("Salvar Empréstimo")

    if enviado:
        if chave and usuario:
            nova_linha = pd.DataFrame([{
                "Chave": chave,
                "Usuário/Chapa": usuario,
                "Status": "Emprestado",
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            dados = pd.concat([dados, nova_linha], ignore_index=True)
            salvar_dados(dados, ARQUIVO_DADOS)

            nova_hist = pd.DataFrame([{
                "Chave": chave,
                "Usuário/Chapa": usuario,
                "Ação": "Emprestado",
                "Status": "Emprestado",
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            historico = pd.concat([historico, nova_hist], ignore_index=True)
            salvar_dados(historico, ARQUIVO_HISTORICO)
            st.success("✅ Empréstimo registrado!")
        else:
            st.warning("Preencha todos os campos!")

# ==============================
# 🔁 Registrar Devolução
# ==============================
st.markdown("---")
st.subheader("🔁 Registrar Devolução")

with st.form("devolucao"):
    chave_dev = st.text_input("Chave a devolver")
    usuario_dev = st.text_input("Usuário/Chapa da devolução")
    enviar_dev = st.form_submit_button("Registrar Devolução")

    if enviar_dev:
        if chave_dev and usuario_dev:
            if chave_dev in dados["Chave"].values:
                dados.loc[dados["Chave"] == chave_dev, "Status"] = "Devolvido"
                salvar_dados(dados, ARQUIVO_DADOS)

                nova_hist = pd.DataFrame([{
                    "Chave": chave_dev,
                    "Usuário/Chapa": usuario_dev,
                    "Ação": "Devolvido",
                    "Status": "Devolvido",
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }])
                historico = pd.concat([historico, nova_hist], ignore_index=True)
                salvar_dados(historico, ARQUIVO_HISTORICO)
                st.success("🔙 Devolução registrada!")
            else:
                st.warning("❌ Chave não encontrada!")
        else:
            st.warning("Preencha todos os campos!")

# ==============================
# ⏱️ Histórico de movimentações
# ==============================
st.markdown("---")
st.subheader("⏱️ Histórico de Movimentações")

if not historico.empty:
    st.dataframe(historico, width="stretch")
    st.download_button("📥 Baixar histórico (CSV)", historico.to_csv(index=False).encode("utf-8"), "historico_chaves.csv")
else:
    st.info("📂 Nenhum histórico encontrado ainda.")

