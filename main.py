import streamlit as st
import pandas as pd
import io
from datetime import date

# --- Configuração da Página ---
st.set_page_config(
    page_title="Comparador de Planilhas de Processos",
    page_icon="📊",
    layout="wide"
)

# --- Função para converter DataFrame para Excel em memória ---
@st.cache_data
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultado')
    processed_data = output.getvalue()
    return processed_data

# --- Título e Descrição do Aplicativo ---
st.title("📊 Comparador de Planilhas de Processos")
st.write(
    "Esta ferramenta compara duas planilhas de processos em formato XLSX. "
    "Ela filtra a primeira planilha (completa) com base nos processos existentes na segunda planilha (filtro), "
    "gera um relatório e permite o download do resultado."
)

# --- Seção de Upload de Arquivos ---
st.header("1. Faça o Upload das Planilhas")

col1, col2 = st.columns(2)

with col1:
    uploaded_file_completa = st.file_uploader(
        "**Planilha Completa** (com as colunas 'PAR OU ÍMPAR' e 'OBSERVAÇÃO')",
        type=['xlsx']
    )

with col2:
    uploaded_file_filtro = st.file_uploader(
        "**Planilha de Filtro** (sem as duas últimas colunas)",
        type=['xlsx']
    )

# --- Lógica Principal do Aplicativo ---
if uploaded_file_completa is not None and uploaded_file_filtro is not None:
    try:
        # Carrega as planilhas
        df_completa = pd.read_excel(uploaded_file_completa)
        df_filtro = pd.read_excel(uploaded_file_filtro)

        # --- CORREÇÃO: Conversão explícita de tipo para evitar erro de serialização ---
        # Garante que a coluna 'OBSERVAÇÃO' seja tratada como texto (string).
        # Isso evita o aviso do Arrow ao lidar com colunas de tipo 'object' com dados mistos.
        if 'OBSERVAÇÃO' in df_completa.columns:
            # .fillna('') transforma células vazias (NaN) em texto vazio ""
            # .astype(str) converte todos os valores (incluindo números) para texto.
            df_completa['OBSERVAÇÃO'] = df_completa['OBSERVAÇÃO'].fillna('').astype(str)

        if 'PROCESSO' not in df_completa.columns or 'PROCESSO' not in df_filtro.columns:
            st.error("Erro: A coluna 'PROCESSO' não foi encontrada em uma ou ambas as planilhas. Verifique os arquivos.")
        else:
            st.success("Planilhas carregadas com sucesso! Iniciando a comparação...")

            # --- Processamento e Comparação ---
            processos_a_manter = df_filtro['PROCESSO'].unique()
            df_final = df_completa[df_completa['PROCESSO'].isin(processos_a_manter)].copy()

            # --- Cálculo das Métricas ---
            set_processos_completa = set(df_completa['PROCESSO'].unique())
            set_processos_filtro = set(df_filtro['PROCESSO'].unique())

            processos_removidos = set_processos_completa - set_processos_filtro
            qtd_despachados = len(processos_removidos)

            processos_novos = set_processos_filtro - set_processos_completa
            qtd_novos = len(processos_novos)

            # --- Exibição dos Resultados ---
            st.header("2. Resultados da Comparação")
            st.subheader("Quadro Comparativo")
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            col_metric1.metric("Total de Processos na Planilha Original", len(set_processos_completa))
            col_metric2.metric("Total de Processos na Planilha de Filtro", len(set_processos_filtro))
            col_metric3.metric(
                label="Processos Despachados (Removidos)",
                value=qtd_despachados,
                help="Processos que estavam na planilha original mas não estão na planilha de filtro."
            )
            col_metric4.metric(
                label="Novos Processos",
                value=qtd_novos,
                help="Processos que estão na planilha de filtro mas não estavam na planilha original."
            )
            st.metric("Total de Processos na Planilha Final (Resultado)", len(df_final))

            # --- Download da Planilha Final ---
            st.header("3. Download do Resultado")

            excel_data = to_excel(df_final)

            data_hoje = date.today().strftime("%Y-%m-%d") 
            nome_arquivo_final = f"planilha_final_comparada_{data_hoje}.xlsx"

            st.download_button(
                label="📥 Baixar Planilha Final em XLSX",
                data=excel_data,
                file_name=nome_arquivo_final,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            with st.expander("Ver pré-visualização da planilha final"):
                st.dataframe(df_final)

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os arquivos: {e}")
        st.warning("Verifique se os arquivos estão no formato XLSX correto e não estão corrompidos.")