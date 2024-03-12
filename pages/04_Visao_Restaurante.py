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
st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
#st.set_page_config(page_title="Cities", page_icon="🏙️", layout="wide")
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



top_n = st.sidebar.slider(
        "Selecione a quantidade de Restaurantes que deseja visualizar", 1, 20, 10 )

cuisines = st.sidebar.multiselect(
        "Escolha os Tipos de Culinária ",
        df.loc[:, "cuisines"].unique().tolist(),
        default=[
            "Home-made",
            "BBQ",
            "Japanese",
            "Brazilian",
            "Arabian",
            "American",
            "Italian",],)

#===============================================================
#                         Função
#===============================================================



def top_restaurants(countries, cuisines, top_n):
    df = df1
    
    cols = [
        "restaurant_id",
        "restaurant_name",
        "country_name",
        "city",
        "cuisines",
        "average_cost_for_two",
        "aggregate_rating",
        "votes",]

    lines = (df["cuisines"].isin(cuisines)) & (df["country_name"].isin(countries))

    dataframe = df.loc[lines, cols].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False, True])

    return dataframe.head(top_n)
    
#===============================================================
#                        Menu de paginas 
#===============================================================


st.markdown("# :knife_fork_plate: Visão Tipos de Cusinhas")


cols = [    "restaurant_id",
            "restaurant_name",
            "country_name",
            "city",
            "cuisines",
            "average_cost_for_two",
            "aggregate_rating",
            "votes",] 

lines = (df["cuisines"].isin(cuisines)) & (df["country_name"].isin(countries))
    
dataframe = df.loc[lines, cols].sort_values(
            ["aggregate_rating", "restaurant_id"], ascending=[False, True])


st.markdown(f"## Melhores Restaurantes dos Principais tipos Culinários")

df = df1

cuisines = {"Italian": "",
            "American": "",
            "Arabian": "",
            "Japanese": "",
            "Brazilian": "",}

cols = [
        "restaurant_id",
        "restaurant_name",
        "country_name",
        "city",
        "cuisines",
        "average_cost_for_two",
        "currency",
        "aggregate_rating",
        "votes",]

for key in cuisines.keys():
    lines = df["cuisines"] == key

    cuisines[key] = ( df.loc[lines, cols]
            .sort_values(["aggregate_rating", "restaurant_id"], ascending=[False, True])
            .iloc[0, :]
            .to_dict())

with st.container():
    italian, american, arabian, japonese, brazilian = st.columns(5)
    with italian: st.metric(
                label=f'Italiana: {cuisines["Italian"]["restaurant_name"]}',
                value=f'{cuisines["Italian"]["aggregate_rating"]}/5.0',
                help=f"""
                País: {cuisines["Italian"]['country_name']}\n
                Cidade: {cuisines["Italian"]['city']}\n
                Média Prato para dois: {cuisines["Italian"]['average_cost_for_two']} ({cuisines["Italian"]['currency']})
                """,)
    with american: st.metric(
                label=f'Italiana: {cuisines["American"]["restaurant_name"]}',
                value=f'{cuisines["American"]["aggregate_rating"]}/5.0',
                help=f"""
                País: {cuisines["American"]['country_name']}\n
                Cidade: {cuisines["American"]['city']}\n
                Média Prato para dois: {cuisines["American"]['average_cost_for_two']} ({cuisines["American"]['currency']})
                """,)
    
    with arabian: st.metric(
                label=f'Italiana: {cuisines["Arabian"]["restaurant_name"]}',
                value=f'{cuisines["Arabian"]["aggregate_rating"]}/5.0',
                help=f"""
                País: {cuisines["Arabian"]['country_name']}\n
                Cidade: {cuisines["Arabian"]['city']}\n
                Média Prato para dois: {cuisines["Arabian"]['average_cost_for_two']} ({cuisines["Arabian"]['currency']})
                """,)
    
    with japonese: st.metric(
                label=f'Italiana: {cuisines["Japanese"]["restaurant_name"]}',
                value=f'{cuisines["Japanese"]["aggregate_rating"]}/5.0',
                help=f"""
                País: {cuisines["Japanese"]['country_name']}\n
                Cidade: {cuisines["Japanese"]['city']}\n
                Média Prato para dois: {cuisines["Japanese"]['average_cost_for_two']} ({cuisines["Japanese"]['currency']})
                """,)
    
    with brazilian: st.metric(
                label=f'Italiana: {cuisines["Brazilian"]["restaurant_name"]}',
                value=f'{cuisines["Brazilian"]["aggregate_rating"]}/5.0',
                help=f"""
                País: {cuisines["Brazilian"]['country_name']}\n
                Cidade: {cuisines["Brazilian"]['city']}\n
                Média Prato para dois: {cuisines["Brazilian"]['average_cost_for_two']} ({cuisines["Brazilian"]['currency']})
                """,)

#==================================================================================================================================

st.markdown(f"## Top {top_n} Restaurantes")

st.dataframe(top_restaurants(countries, cuisines, top_n))


best, worst = st.columns(2)

with best:
    df = df1
    
    lines = df["country_name"].isin(countries)
    
    grouped_df = (
            df.loc[lines, ["aggregate_rating", "cuisines"]]
            .groupby("cuisines")
            .mean()
            .sort_values("aggregate_rating", ascending=False)
            .reset_index()
            .head(top_n) )
    
    fig = px.bar(
            grouped_df.head(top_n),
            x="cuisines",
            y="aggregate_rating",
            text="aggregate_rating",
            text_auto=".2f",
            title=f"Top {top_n} Melhores Tipos de Culinárias",
            labels={"cuisines": "Tipo de Culinária","aggregate_rating": "Média da Avaliação Média",},)
    
    st.plotly_chart(fig, use_container_width=True)

with worst:
        
    lines = df["country_name"].isin(countries)
    
    grouped_df = (
            df1.loc[lines, ["aggregate_rating", "cuisines"]]
            .groupby("cuisines")
            .mean()
            .sort_values("aggregate_rating", ascending=True)
            .reset_index()
            .head(top_n))
    
    fig = px.bar(
            grouped_df.head(top_n),
            x="cuisines",
            y="aggregate_rating",
            text="aggregate_rating",
            text_auto=".2f",
            title=f"Top {top_n} Piores Tipos de Culinárias",
            labels={"cuisines": "Tipo de Culinária","aggregate_rating": "Média da Avaliação Média",},)
    
    st.plotly_chart(fig, use_container_width=True)


#mask_cuisines = df["cuisines"].apply(lambda x: any(cuisine in x.split(", ") for cuisine in cuisines))











