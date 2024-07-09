import pandas as pd
import numpy as np
import re
import plotly.express as px
import inflection
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from PIL import Image
from streamlit_folium import folium_static

df = pd.read_csv('dataset/zomato.csv')

# Limpeza de dados
df.isna().sum()
#Preenchimento do nome dos países
COUNTRIES = {1: "India",14: "Australia",30: "Brazil",37: "Canada",94: "Indonesia",148: "New Zeland",162: "Philippines",
166: "Qatar",184: "Singapure",189: "South Africa",191: "Sri Lanka",208: "Turkey",214: "United Arab Emirates",215: "England",
216: "United States of America",}
def country_name(country_id):
  return COUNTRIES[country_id]

#Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"

#Criação do nome das Cores
COLORS = {"3F7E00": "darkgreen","5BA829": "green","9ACD32": "lightgreen","CDD614": "orange",
"FFBA00": "red","CBCBC8": "darkred","FF7800": "darkred",}
def color_name(color_code):
  return COLORS[color_code]

#Renomear as colunas do DataFrame
def rename_columns(dataframe):
  df = dataframe.copy()
  title = lambda x: inflection.titleize(x)
  snakecase = lambda x: inflection.underscore(x)
  spaces = lambda x: x.replace(" ", "")
  cols_old = list(df.columns)
  cols_old = list(map(title, cols_old))
  cols_old = list(map(spaces, cols_old))
  cols_new = list(map(snakecase, cols_old))
  df.columns = cols_new
  return df

# Aplicando as transformações
df['Country Name'] = df['Country Code'].apply(country_name)
df['Price Type'] = df['Price range'].apply(create_price_tye)
df['Rating Color Name'] = df['Rating color'].apply(color_name)
df = rename_columns(df)

#df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
df["cuisines"] = df["cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)

#retirar linhas duplicadas
df = df.dropna()

df = df.drop_duplicates()

df1 = df.copy()
#===============================================================
#                         Menu de paginas 
#===============================================================
#st.set_page_config(page_title="Countries", page_icon="", layout="wide")
st.set_page_config(page_title="Home", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
#===============================================================
#                         Side bar
#===============================================================
# Colocação de Logo e inicio com o nome Fome zero
image_path = 'logo.png'
col1, col2 = st.sidebar.columns([1, 4], gap="small")
col1.image(image_path, width=35)
col2.markdown("# Fome Zero")

# Filtros para interação
st.sidebar.markdown("## Filtros")

countries = st.sidebar.multiselect(
        "Escolha os Paises que Deseja visualizar as Informações",
        df.loc[:, "country_name"].unique().tolist(),
        default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"],)

#===============================================================
#                        Meio
#===============================================================

st.markdown("# :earth_americas: Visão Países")
#-------------------------------------------------------------------------------------------------------------------------------------
# Número de Cidades por País'
df_filtered = df1[df1['country_name'].isin(countries)]

# Conta o número de cidades únicas por país no DataFrame filtrado
cidades_por_pais = df_filtered.groupby('country_name')['city'].nunique().reset_index()

# Ordena os países pelo número de cidades de forma descendente
cidades_por_pais = cidades_por_pais.sort_values(by='city', ascending=False)

# Cria um gráfico de barras com Plotly Express
fig = px.bar(cidades_por_pais, 
             x='country_name', 
             y='city', 
             title='Número de Cidades por País',
             labels={'city':'Número de Cidades', 'country_name':'País'},
             color='city',  # Usa o número de cidades para colorir as barras
             color_continuous_scale=px.colors.sequential.Viridis)  # Escolhe uma escala de cores

# Melhora a formatação do gráfico
fig.update_layout(xaxis_title='País',
                  yaxis_title='Número de Cidades',
                  coloraxis_showscale=False)  # Oculta a legenda de cores para simplificar

# Para incorporar o gráfico em uma aplicação Streamlit, use:
st.plotly_chart(fig)

#-------------------------------------------------------------------------------------------------------------------------------------
col1,col2 = st.columns([2, 2])

with col1:
    # Contagem de restaurantes por país
    restaurantes_por_pais = df1['country_name'].value_counts()
    
    # Converte a série em um DataFrame para facilitar a manipulação e visualização
    df_restaurantes_por_pais = restaurantes_por_pais.reset_index()
    df_restaurantes_por_pais.columns = ['País', 'Número de Restaurantes']
    
    # Você pode ajustar este número para mostrar mais ou menos países
    N = 4
    
    # Seleciona os top N países com mais restaurantes
    df_top_n_restaurantes = df_restaurantes_por_pais.head(N)
    
    # Exibe a tabela com Streamlit
    st.write(f"Países com mais restaurantes registrados:")
    st.table(df_top_n_restaurantes)
    
#-------------------------------------------------------------------------------------------------------------------------------------
with col2:
    restaurantes_preco_4 = df1[df1['aggregate_rating'] >= 4]
    
    # Conta o número de restaurantes com preço 4 por país
    restaurantes_preco_4_por_pais = restaurantes_preco_4['country_name'].value_counts()
    
    # Transforma a série em um DataFrame para melhor manipulação
    df_restaurantes_preco_4_por_pais = restaurantes_preco_4_por_pais.reset_index()
    df_restaurantes_preco_4_por_pais.columns = ['País', 'Número de Restaurantes com Preço 4']
    
    # Seleciona os 4 primeiros países
    df_top_4_restaurantes_preco_4 = df_restaurantes_preco_4_por_pais.head(4)
    
    # Usa o Streamlit para exibir a tabela
    st.write('Países com mais restaurantes com preço igual a 4')
    st.table(df_top_4_restaurantes_preco_4)
#-------------------------------------------------------------------------------------------------------------------------------------
# Resdondendo perguntas 
col1, col2, col3 = st.columns([1.2, 1, 1])

col1.metric("Maior quantidade de avaliações registrada", (df1.loc[:, ['votes', 'country_name'] ]                                                                                                      .groupby('country_name')
                                                               .mean()
                                                               .sort_values('votes', ascending=False)
                                                               .reset_index()).iloc[0, 0],)

col2.metric("País a maior nota média registrada", (df1.loc[:, ['aggregate_rating', 'country_name'] ]
                                                          .groupby('country_name')
                                                          .mean()
                                                          .sort_values('aggregate_rating', ascending=False)
                                                          .reset_index()).iloc[0, 0],)

col3.metric("País com menor média de notas", (df1.loc[:, ['aggregate_rating', 'country_name'] ]
                                                                                 .groupby('country_name')
                                                                                 .mean()
                                                                                 .sort_values('aggregate_rating', ascending=True)
                                                                                 .reset_index()).iloc[0, 0],)

#-------------------------------------------------------------------------------------------------------------------------------------


media_custo_por_pais = df_filtered.groupby('country_name')['average_cost_for_two'].mean().reset_index().head()

# Renomear as colunas para melhor entendimento
media_custo_por_pais.columns = ['country_name', 'average_cost_for_two']

# Criando o gráfico com Plotly
fig = px.bar(media_custo_por_pais, x='average_cost_for_two', y='country_name', orientation='h', title='Média do Custo de um Prato para Duas Pessoas por País', labels={'country_name': 'País', 'average_cost_for_two': 'Média do Custo'})
fig.update_layout(yaxis={'categoryorder':'total ascending'})

# Usar Streamlit para exibir o gráfico
st.plotly_chart(fig)









