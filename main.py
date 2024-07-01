import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

st.set_page_config(page_title="100 dias.", page_icon=":tada:")

st.title(":tada:100 dias de HOJE!")

hoje = datetime.date.today().strftime(r"%d/%m/%Y")

def load_excel(file):
    return pd.read_excel(file)

def compare_and_update(old_df, new_df):
    # Identificar processos PAR e ÍMPAR na nova planilha
    new_df['TIPO'] = new_df['PROCESSO'].apply(lambda x: 'PAR' if int(x.split('-')[0]) % 2 == 0 else 'ÍMPAR')

    # Adicionar observações da planilha antiga na nova planilha
    new_df = pd.merge(new_df, old_df[['PROCESSO', 'TAREFAS']], on='PROCESSO', how='left', suffixes=('', '_OLD'))

    # Manter apenas a coluna TAREFAS da nova planilha, renomeando-a para Y se necessário
    new_df['TAREFAS'] = new_df['TAREFAS'].combine_first(new_df['TAREFAS_OLD'])
    new_df = new_df.drop(columns=['TAREFAS_OLD'])

    # Reorganizar colunas para que TIPO esteja ao lado direito de PROCESSO e TAREFAS seja a última
    cols = list(new_df.columns)
    cols.insert(cols.index('PROCESSO') + 1, cols.pop(cols.index('TIPO')))
    cols.append(cols.pop(cols.index('TAREFAS')))
    new_df = new_df[cols]

    return new_df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

def main():
    st.title('Comparador de Planilhas de Processos:')

    old_file = st.file_uploader('Upload da Planilha Antiga', type='xlsx')
    new_file = st.file_uploader('Upload da Planilha Nova', type='xlsx')

    if old_file and new_file:
        old_df = load_excel(old_file)
        new_df = load_excel(new_file)

        result_df = compare_and_update(old_df, new_df)

        st.write('### Planilha Comparada')
        st.dataframe(result_df)

        excel_data = convert_df_to_excel(result_df)
        st.download_button(label='Download da Planilha Comparada',
                           data=excel_data,
                           file_name=f'planilha_100dias_comparada_{hoje}.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    main()
