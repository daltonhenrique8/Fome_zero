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
#st.set_page_config(page_title="Home", page_icon="", layout="wide")
st.set_page_config(page_title="Home", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

#===============================================================
#                         Função
#===============================================================
def create_map(data):
    f = folium.Figure(width=1920, height=1080)

    m = folium.Map(max_bounds=True).add_to(f)

    marker_cluster = MarkerCluster().add_to(m)

    for _, line in df1.iterrows():

        name = line["restaurant_name"]
        price_for_two = line["average_cost_for_two"]
        cuisine = line["cuisines"]
        currency = line["currency"]
        rating = line["aggregate_rating"]
        color = f'{line["rating_color_name"]}'

        html = "<p><strong>{}</strong></p>"
        html += "<p>Price: {},00 ({}) para dois"
        html += "<br />Type: {}"
        html += "<br />Aggragate Rating: {}/5.0"
        html = html.format(name, price_for_two, currency, cuisine, rating)

        popup = folium.Popup(
            folium.Html(html, script=True),
            max_width=500,)

        folium.Marker(
            [line["latitude"], line["longitude"]],
            popup=popup,
            icon=folium.Icon(color=color, icon="home", prefix="fa"),
        ).add_to(marker_cluster)

    folium_static(m, width=700, height=500)
    
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

# Dowload do arquivo ja tratado com a limpeza de dados
st.sidebar.markdown("### Dados Tratados")

processed_data = df1

st.sidebar.download_button(
    label="Download",
    data=df1.to_csv(index=False, sep=";"),
    file_name="zomato.csv",
    mime="text/csv",)

#===============================================================
#                         Meio
#===============================================================


st.markdown("# Fome Zero!")

st.markdown("## O Melhor lugar para encontrar seu mais novo restaurante favorito!")

st.markdown("### Temos as seguintes marcas dentro da nossa plataforma:")

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 1])
#col1, col2, col3, col4, col5 = st.columns(5)
    #restaurants, countries, cities, ratings, cuisines
col1.metric("Restaurantes Cadastrados", df1['restaurant_id'].nunique(),)

col2.metric("Países Cadastrados", df1['country_name'].nunique(),)

col3.metric("Cidades Cadastrados", df1['city'].nunique(),)

total_avaliacoes = df1['votes'].sum()
total_avaliacoes_formatado = "{:,}".format(total_avaliacoes).replace(",", ".")
col4.metric("Avaliações Feitas na Plataforma", total_avaliacoes_formatado,)

col5.metric("Tipos de Culinárias Oferecidas", df1['cuisines'].nunique(),)


#Fazendo o mapa com base na função create_map
map_df = df1.loc[df1["country_name"].isin(countries), :]
create_map(map_df)
