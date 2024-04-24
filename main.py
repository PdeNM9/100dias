import pandas as pd
import streamlit as st

st.set_page_config(page_title="100 dias.", page_icon=":tada:")

st.title(":tada:100 dias de HOJE!")

uploaded_file = st.file_uploader("Arquivo", type="xlsx")

if uploaded_file:
    # Ler o arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Selecionando as colunas necessárias
    if {'DESCRIÇÃO CLASSE CNJ', 'PROCESSO', 'VALOR DA CAUSA', 'QTDE DIAS'}.issubset(df.columns):
        df = df[['DESCRIÇÃO CLASSE CNJ', 'PROCESSO', 'VALOR DA CAUSA', 'QTDE DIAS']]

        # Adicionando a coluna PAR ou ÍMPAR
        # A coluna PROCESSO é assumida como uma string para que a função ESQUERDA possa ser aplicada
        df['PAR ou ÍMPAR'] = df['PROCESSO'].apply(lambda x: "PAR" if pd.to_numeric(x.split("-")[0]) % 2 == 0 else "ÍMPAR")

        # Botão para filtrar entre pares e ímpares
        filter_option = st.radio("Filtrar por:", ('Todos', 'Pares', 'Ímpares'))

        # Contando pares e ímpares
        count_par = df[df['PAR ou ÍMPAR'] == 'PAR'].shape[0]
        count_impar = df[df['PAR ou ÍMPAR'] == 'ÍMPAR'].shape[0]

        if filter_option == 'Pares':
            df = df[df['PAR ou ÍMPAR'] == 'PAR']
            st.write(f"Quantidade de Pares: {count_par}")
            st.write(f"Quantidade de Ímpares: {count_impar}")
        elif filter_option == 'Ímpares':
            df = df[df['PAR ou ÍMPAR'] == 'ÍMPAR']
            st.write(f"Quantidade de Pares: {count_par}")
            st.write(f"Quantidade de Ímpares: {count_impar}")

        # Mostra o DataFrame após filtro
        st.write(df)

        # Mostra quantidade total de pares e ímpares se a opção "Todos" for selecionada
        if filter_option == 'Todos':
            st.write(f"Quantidade de Pares: {count_par}")
            st.write(f"Quantidade de Ímpares: {count_impar}")

    else:
        st.error("O arquivo não contém as colunas necessárias.")
else:
    st.info("Por favor, carregue um arquivo.")

