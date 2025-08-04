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
    "adiciona processos novos, gera um relatório e permite o download do resultado."
)

# --- Seção de Upload de Arquivos ---
st.header("1. Faça o Upload das Planilhas")

col1, col2 = st.columns(2)

with col1:
    uploaded_file_completa = st.file_uploader(
        "**Planilha Completa Original** (com 'PAR OU ÍMPAR' e 'OBSERVAÇÃO')",
        type=['xlsx']
    )

with col2:
    uploaded_file_filtro = st.file_uploader(
        "**Planilha de Filtro/Atualizada** (sem as duas últimas colunas)",
        type=['xlsx']
    )

# --- Lógica Principal do Aplicativo ---
if uploaded_file_completa is not None and uploaded_file_filtro is not None:
    try:
        # Carrega as planilhas
        df_completa_original = pd.read_excel(uploaded_file_completa)
        df_filtro_atualizada = pd.read_excel(uploaded_file_filtro)

        # --- MELHORIA: Normalizar nomes das colunas para maior robustez ---
        df_completa_original.columns = [col.strip().upper() for col in df_completa_original.columns]
        df_filtro_atualizada.columns = [col.strip().upper() for col in df_filtro_atualizada.columns]


        if 'PROCESSO' not in df_completa_original.columns or 'PROCESSO' not in df_filtro_atualizada.columns:
            st.error("Erro: A coluna 'PROCESSO' não foi encontrada em uma ou ambas as planilhas. Verifique os arquivos.")
        else:
            st.success("Planilhas carregadas com sucesso! Iniciando a comparação...")

            # --- MELHORIA: Normalizar dados da coluna 'PROCESSO' ---
            df_completa_original['PROCESSO'] = df_completa_original['PROCESSO'].astype(str).str.strip()
            df_filtro_atualizada['PROCESSO'] = df_filtro_atualizada['PROCESSO'].astype(str).str.strip()

            # Garante que a coluna 'OBSERVAÇÃO' na planilha original seja tratada como texto.
            if 'OBSERVAÇÃO' in df_completa_original.columns:
                df_completa_original['OBSERVAÇÃO'] = df_completa_original['OBSERVAÇÃO'].fillna('').astype(str)
            # Garante que a coluna 'PAR OU ÍMPAR' na planilha original seja tratada como texto (boa prática).
            if 'PAR OU ÍMPAR' in df_completa_original.columns:
                df_completa_original['PAR OU ÍMPAR'] = df_completa_original['PAR OU ÍMPAR'].fillna('').astype(str)

            # --- Identificação de Processos ---
            set_processos_completa = set(df_completa_original['PROCESSO'].unique())
            set_processos_filtro = set(df_filtro_atualizada['PROCESSO'].unique())

            processos_removidos = set_processos_completa - set_processos_filtro
            qtd_despachados = len(processos_removidos)

            processos_novos_identificados = set_processos_filtro - set_processos_completa
            qtd_novos = len(processos_novos_identificados)

            # --- Lógica de Criação da DF_FINAL (Está correta) ---

            # 1. Processos da planilha completa que AINDA ESTÃO na planilha de filtro/atualizada
            df_mantidos_com_dados_completos = df_completa_original[
                df_completa_original['PROCESSO'].isin(set_processos_filtro)
            ].copy()

            # 2. Processos que são NOVOS (estão no filtro/atualizada, mas não na completa original)
            df_novos_para_adicionar = df_filtro_atualizada[
                df_filtro_atualizada['PROCESSO'].isin(processos_novos_identificados)
            ].copy()

            # 3. Concatenar os dois DataFrames
            df_final = pd.concat([df_mantidos_com_dados_completos, df_novos_para_adicionar], ignore_index=True, sort=False)

            # 4. Ajuste Pós-Concatenação para as colunas extras
            colunas_extras = ['PAR OU ÍMPAR', 'OBSERVAÇÃO']
            for col in colunas_extras:
                if col in df_final.columns:
                    df_final[col] = df_final[col].fillna('').astype(str)
                else: # Se a coluna não existia na original, cria como vazia para consistência
                    df_final[col] = ''

            # --- MELHORIA: Adicionar ordenação ao resultado final ---
            # Reordena o dataframe final com base na coluna PROCESSO para um resultado mais limpo
            if 'PROCESSO' in df_final.columns:
                df_final = df_final.sort_values(by='PROCESSO').reset_index(drop=True)

            # --- Exibição dos Resultados ---
            st.header("2. Resultados da Comparação")
            st.subheader("Quadro Comparativo")
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            col_metric1.metric("Total de Processos na Planilha Original", len(set_processos_completa))
            col_metric2.metric("Total de Processos na Planilha de Filtro/Atualizada", len(set_processos_filtro))
            col_metric3.metric(
                label="Processos Despachados (Removidos)",
                value=qtd_despachados,
                help="Processos que estavam na planilha original mas não estão na de filtro."
            )
            col_metric4.metric(
                label="Novos Processos (Adicionados)",
                value=qtd_novos,
                help="Processos que estão na planilha de filtro mas não estavam na original."
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

            with st.expander("Ver pré-visualização da planilha final (primeiras 100 linhas)"):
                st.dataframe(df_final.head(100))

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os arquivos: {e}")
        st.exception(e)
        st.warning("Verifique se os arquivos estão no formato XLSX correto e não estão corrompidos. Verifique também se a coluna 'PROCESSO' existe em ambas.")