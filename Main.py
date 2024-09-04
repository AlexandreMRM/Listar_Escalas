import pandas as pd
import mysql.connector
import streamlit as st
import plotly.express as px
from datetime import date

# Parametros de Login AWS
@st.cache(ttl=600)
def BD_Phoenix():
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    # Script MySql para requests
    cursor.execute(
        'SELECT * FROM vw_payment_guide'
    )
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    #df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

    cols = ['Data da Escala', 
        'Escala',
        'Guia', 
        'Data Execucao', 
        'Servico', 
        'Data | Horario Apresentacao', 
        'Status do Servico'
    ]
    df = df[cols]
    return df
st.set_page_config(layout='wide')
if 'df' not in st.session_state:
    st.session_state.df = BD_Phoenix()
df = st.session_state.df

#lista dos guias - Para o selectbox do streamlit
lista_guias = df['Guia'].dropna().unique().tolist()
lista_guias.sort()
lista_guias.insert(0, "--- Todos ---")
lista_servico = df['Servico'].dropna().unique().tolist()
lista_servico.sort()
lista_servico.insert(0, "--- Todos ---")


st.title('Listar Escalas')
st.markdown("""
             <style>
            .stApp{
                background-color: #047c6c;
            }
            h1{
                font-size: 40pt;
                color: #d17d7f;
            }
            h2, h3, .stMarkdown, .stRadio label, .stSelectbox label{
                font-size: 10pt;
                color: #74c4bc;
            }
            .stDateInput label {
                font-size: 20pt;
                color: #74c4bc;
            }
            <style>
""", unsafe_allow_html=True)
st.session_state.df = df

col1, col2 = st.columns([2,6])

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        data_ini = st.date_input('Data Inicio', value=date(2024,1,1), format='DD/MM/YYYY')
    with col1_2:
        data_fim = st.date_input('Data Fim', value=date(2025,1,1), format='DD/MM/YYYY')
    selecionar_guia = st.selectbox("Selecione o Guia:", lista_guias)
    selecionar_servico = st.selectbox("Selecione o Serviço: ", lista_servico)
    botao_filtrar = st.button("Filtrar")

if botao_filtrar:
    resultado_filtrado = df[
        (df['Data da Escala'] >= data_ini) &
        (df['Data da Escala'] <= data_fim)
    ]

    #Filtrar por Guia se não for TODOS
    if selecionar_guia != "--- Todos ---":
        resultado_filtrado = resultado_filtrado[resultado_filtrado['Guia'] == selecionar_guia]

    #Filtrar por Serviço se não for TODOS
    if selecionar_servico != "--- Todos ---":
        resultado_filtrado = resultado_filtrado[resultado_filtrado['Servico'] == selecionar_servico]

    resultado_filtrado = resultado_filtrado[['Guia', 'Data da Escala','Servico', 'Status do Servico', 'Escala' ]]

    resultado_filtrado = resultado_filtrado.drop_duplicates(subset=['Servico', 'Escala'])    
    resultado_filtrado = resultado_filtrado.sort_values(by='Data da Escala')
    resultado_filtrado['Data da Escala'] = pd.to_datetime(resultado_filtrado['Data da Escala']).dt.strftime('%d/%m/%Y')



    with col2:
        col2_1, col2_2 = st.columns([4,2])
        with col2_1:
            st.write('Resultado')
            st.dataframe(resultado_filtrado, hide_index=True, use_container_width=True)
        with col2_2:
            if selecionar_guia != "--- Todos ---":
                contador_servicos = resultado_filtrado['Servico'].value_counts().reset_index()
                contador_servicos.columns = ['Servico', 'Quantidade']

                st.write('Contador de Serviços')
                st.dataframe(contador_servicos, hide_index=True, use_container_width=True)
                



