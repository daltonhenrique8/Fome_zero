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
st.set_page_config(page_title="Cities", page_icon="", layout="centered")
#st.set_page_config(page_title="Home", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
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


st.markdown("# :cityscape: Visão Cidades")

filtered_df = df1[df1['country_name'].isin(countries)]
#with st.container(border=900):
#Numero de quantos cidades aparece 
N = 120
# Agrupando e contando o número de restaurantes por cidade
restaurantes_por_cidade = (df1[df1['country_name'].isin(countries)]
                              .groupby('city')
                              .count()
                              .sort_values('restaurant_id', ascending=False)
                              .reset_index().head(N))
    
# Renomeando a coluna para refletir o conteúdo corretamente
restaurantes_por_cidade.rename(columns={'restaurant_id': 'numero_de_restaurantes'}, inplace=True)
    
# Criando um gráfico de barras com Plotly Express
fig = px.bar(restaurantes_por_cidade, x='city', y='numero_de_restaurantes',
                 title='Número de Restaurantes por Cidade',
                 labels={'city': 'Cidade', 'numero_de_restaurantes': 'Número de Restaurantes'},
                 color='numero_de_restaurantes',
                 color_continuous_scale=px.colors.sequential.Viridis)
    
# Ajustando o layout para melhorar a visualização
fig.update_layout(xaxis_title="Cidade",
                      yaxis_title="Número de Restaurantes",
                      coloraxis_showscale=True,
                      height=400,
                      width=1290 )
    
# Usando Streamlit para exibir o gráfico
st.plotly_chart(fig)
#========================================================================================================================================
with st.container():
    col1,col2 = st.columns([2, 1])
    
    with col1:
        #Numero de quantos cidades aparece 
        N = 4
        # Agrupando e contando o número de restaurantes por cidade     
        restaurantes_por_cidade = (filtered_df.loc[filtered_df['aggregate_rating'] >= 4, ['restaurant_id', 'city']]
                                             .groupby('city')
                                             .count()
                                             .sort_values('restaurant_id', ascending=False)
                                             .reset_index().head(N))
        
        # Renomeando a coluna para refletir o conteúdo corretamente
        restaurantes_por_cidade.rename(columns={'restaurant_id': 'numero_de_restaurantes'}, inplace=True)
        
        # Criando um gráfico de barras com Plotly Express
        fig = px.bar(restaurantes_por_cidade, x='city', y='numero_de_restaurantes',
                     title='Número de Restaurantes com melhores avaliações',
                     labels={'city': 'Cidade', 'numero_de_restaurantes': 'Número de Restaurantes'},
                     color='numero_de_restaurantes',
                     color_continuous_scale=px.colors.sequential.Viridis)
        
        # Ajustando o layout para melhorar a visualização
        fig.update_layout(xaxis_title="Cidade",
                          yaxis_title="Número de Restaurantes",
                          coloraxis_showscale=True) # Desativa a legenda de cores se não for necessária
        
        # Usando Streamlit para exibir o gráfico
        st.plotly_chart(fig)
    
    with col2:
        #Numero de quantos cidades aparece 
        N = 4
        # Calculando a média do custo para duas pessoas por cidade e ordenando
        custo_medio_por_cidade = (filtered_df.loc[:, ['average_cost_for_two', 'city']]
                                  .groupby('city')
                                  .mean()
                                  .sort_values('average_cost_for_two', ascending=False)
                                  .reset_index().head(N))
        
        # Criando um gráfico de barras com Plotly Express
        fig = px.bar(custo_medio_por_cidade, x='city', y='average_cost_for_two',
                     title='Custo Médio para Duas Pessoas por Cidade',
                     labels={'city': 'Cidade', 'average_cost_for_two': 'Custo Médio para Duas Pessoas'},
                     color='average_cost_for_two',
                     color_continuous_scale=px.colors.sequential.Inferno)
        
        # Ajustando o layout para melhorar a visualização
        fig.update_layout(xaxis_title="Cidade",
                          yaxis_title="Custo Médio para Duas Pessoas",
                          coloraxis_showscale=False,)
                          
        
        # Usando Streamlit para exibir o gráfico
        st.plotly_chart(fig)
#=======================================================================================================================================
with st.container():
    col1,col2 = st.columns([2, 1])
    
    
    with col1:
        #Numero de quantos cidades aparece 
        N = 4
        # Primeiro, calculamos a diversidade de cozinhas por cidade.
        diversidade_cozinhas = (filtered_df.loc[:, ['cuisines', 'city']]
                                .groupby('city')
                                .nunique()
                                .sort_values('cuisines', ascending=False)
                                .reset_index().head(N))
        
        # Agora, vamos criar um gráfico de barras utilizando Plotly Express.
        fig = px.bar(diversidade_cozinhas, 
                     x='city', 
                     y='cuisines', 
                     title='Cidades com culinárias distintas',
                     labels={'city': 'Cidade', 'cuisines': 'Número de Cozinhas Únicas'},
                     color='cuisines',
                     color_continuous_scale=px.colors.sequential.Agsunset)
        
        # Ajustando o layout para uma melhor visualização
        fig.update_layout(xaxis_title="Cidade",
                          yaxis_title="Número de Cozinhas Únicas",
                          coloraxis_colorbar=dict(title="Número de Cozinhas Únicas"))
        
        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig)
    
    
    with col2:
        #Numero de quantos cidades aparece 
        N = 6
        # Filtrando os dados e calculando a quantidade de restaurantes com reserva de mesa por cidade
        restaurantes_reserva = (filtered_df.loc[df1['has_table_booking'] == 1, ['restaurant_id', 'city']]
                                .groupby('city')
                                .count()
                                .sort_values('restaurant_id', ascending=False)
                                .reset_index().head(N))
        
        # Renomeando a coluna para melhor claridade
        restaurantes_reserva.rename(columns={'restaurant_id': 'quantidade_de_restaurantes'}, inplace=True)
        
        # Criando um gráfico de barras com Plotly Express
        fig = px.bar(restaurantes_reserva, 
                     x='city', 
                     y='quantidade_de_restaurantes', 
                     title='Cidades oferecem Reserva de Mesa',
                     labels={'city': 'Cidade', 'quantidade_de_restaurantes': 'Quantidade de Restaurantes'},
                     color='quantidade_de_restaurantes',
                     color_continuous_scale=px.colors.sequential.Viridis)
        
        # Ajustando o layout para melhor visualização
        fig.update_layout(xaxis_title="Cidade",
                          yaxis_title="Quantidade de Restaurantes",
                          coloraxis_colorbar=dict(title="Quantidade de Restaurantes"))
        
        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig)
#=======================================================================================================================================
#Numero de quantos cidades aparece 
    N = 4
# Filtrando os dados para encontrar restaurantes que estão entregando agora e contando por cidade
restaurantes_entregando_agora = (filtered_df.loc[df1['is_delivering_now'] == 1, ['restaurant_id', 'city']]
                                 .groupby('city')
                                 .count()
                                 .sort_values('restaurant_id', ascending=False)
                                 .reset_index().head(N))

# Renomeando a coluna para melhor claridade
restaurantes_entregando_agora.rename(columns={'restaurant_id': 'quantidade_de_restaurantes'}, inplace=True)

# Criando um gráfico de barras com Plotly Express
fig = px.bar(restaurantes_entregando_agora, 
             x='city', 
             y='quantidade_de_restaurantes', 
             title='Cidades com Maior Quantidade de Restaurantes Entregando Agora',
             labels={'city': 'Cidade', 'quantidade_de_restaurantes': 'Quantidade de Restaurantes'},
             color='quantidade_de_restaurantes',
             color_continuous_scale=px.colors.sequential.Inferno)

# Ajustando o layout para melhor visualização
fig.update_layout(xaxis_title="Cidade",
                  yaxis_title="Quantidade de Restaurantes",
                  coloraxis_colorbar=dict(title="Quantidade de Restaurantes"),
                  height=400,
                  width=1290 )

# Exibindo o gráfico no Streamlit
st.plotly_chart(fig)

















