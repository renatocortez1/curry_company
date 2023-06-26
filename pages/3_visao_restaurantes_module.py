# Importando as Bibliotecas:

import pandas as pd
import plotly.express as px
from haversine import haversine as hs
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import numpy as np
import folium
import datetime
from streamlit_folium import folium_static

# --------------------------------------
# Importando o data set:
df_raw = pd.read_csv("train.csv")
df = df_raw.copy()

# Configurando a apresentação da Página:
st.set_page_config(page_title="Visão restaurantes", page_icon="🥫", layout="wide")

# --------------------------------------------------------------------------------------------------
#                                           Funções
# --------------------------------------------------------------------------------------------------


# Função Limpeza do Conjunto de Dados:
def clean_code(df):
    """Esta função tem a responsabilidade de limpar o dataframe

    Tipos de Limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo de coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: Dataframe Sujo
    Output: Dataframe Limpo
    """

    # 1. Remover espaco da string
    # for i in range( len( df ) ):
    #  df.loc[i, 'ID'] = df.loc[i, 'ID'].strip()
    #  df.loc[i, 'Delivery_person_ID'] = df.loc[i, 'Delivery_person_ID'].strip()

    # 1.1 Outra forma de remover o espaço da string:
    df.loc[:, "ID"] = df.loc[:, "ID"].str.strip()
    df.loc[:, "Delivery_person_ID"] = df.loc[:, "Delivery_person_ID"].str.strip()
    df.loc[:, "Road_traffic_density"] = df.loc[:, "Road_traffic_density"].str.strip()
    df.loc[:, "Type_of_order"] = df.loc[:, "Type_of_order"].str.strip()
    df.loc[:, "Type_of_vehicle"] = df.loc[:, "Type_of_vehicle"].str.strip()
    df.loc[:, "City"] = df.loc[:, "City"].str.strip()
    df.loc[:, "Festival"] = df.loc[:, "Festival"].str.strip()

    # 2. ( Conceitos de seleção condicional )
    linhas_vazias = df["Delivery_person_Age"] != "NaN "
    df = df.loc[linhas_vazias, :]
    # 3. Conversao de texto/categoria/string para numeros inteiros
    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype(int)

    # 4.  Conversao de texto/categoria/strings para numeros decimais
    df["Delivery_person_Ratings"] = df["Delivery_person_Ratings"].astype(float)
    # 5. Conversao de texto para data
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y")
    # 6. Remove as linhas da culuna multiple_deliveries que tenham o  conteudo igual a 'NaN '
    linhas_vazias = df["multiple_deliveries"] != "NaN "
    df = df.loc[linhas_vazias, :]
    df["multiple_deliveries"] = df["multiple_deliveries"].astype(int)
    # 7. Comando para remover o texto "conditions" da Coluna Weatherconditions:
    df["Weatherconditions"] = df["Weatherconditions"].apply(
        lambda x: x.split("conditions")[1].strip()
    )
    # 8. Comando para remover o texto de números - Coluna time_taken:
    # Forma da aula:
    df["Time_taken(min)"] = df["Time_taken(min)"].apply(lambda x: x.split("(min) ")[1])
    df["Time_taken(min)"] = df["Time_taken(min)"].astype(int)
    # Forma da lista do monitor:
    # df = df.reset_index( drop=True )
    # for i in range( len( df ) ):
    # df.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df.loc[i, 'Time_taken(min)'] )

    # Retirando os numeros da coluna Time_taken(min) - Forma 1
    # df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x))

    # Retirando os numeros da coluna Time_taken(min) - Forma 2
    # df.loc[0, 'Time_taken(min)'].split(' ' )[1]

    # Retirando os numeros da coluna Time_taken(min) - Forma 3
    # df.loc[0, 'Time_taken(min)'].replace( ('min'), '')

    # 9. Remove os NAN das colunas:
    df = df.loc[df["City"] != "NaN"]
    df = df.loc[df["Weatherconditions"] != "conditions NaN"]
    df = df.loc[df["Road_traffic_density"] != "NaN", :]

    # 10. # Remove os NA que forem np.na
    df = df.dropna()

    return df


# Função Distance:
def distance(df, fig):
    if fig == False:
        cols = [
            "Restaurant_latitude",
            "Restaurant_longitude",
            "Delivery_location_latitude",
            "Delivery_location_longitude",
        ]
        df["distance"] = round(
            df.loc[:, cols].apply(
                lambda x: hs(
                    (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                    (
                        x["Delivery_location_latitude"],
                        x["Delivery_location_longitude"],
                    ),
                ),
                axis=1,
            ),
            3,
        )

        # Cálculo da Média:
        media_distancia = round(df["distance"].mean(), 2)

        return media_distancia

    else:
        cols = [
            "Restaurant_latitude",
            "Restaurant_longitude",
            "Delivery_location_latitude",
            "Delivery_location_longitude",
        ]
        df["distance"] = round(
            df.loc[:, cols].apply(
                lambda x: hs(
                    (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                    (
                        x["Delivery_location_latitude"],
                        x["Delivery_location_longitude"],
                    ),
                ),
                axis=1,
            ),
            3,
        )

        # Cálculo da Média:
        media_distancia = (
            df.loc[:, ["City", "distance"]].groupby("City").mean().reset_index()
        )
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=media_distancia["City"],
                    values=media_distancia["distance"],
                    pull=[0, 0.1, 0],
                )
            ]
        )
        return fig


# Função Média e Desvio do Tempo de entrega em Gráfico:
def avg_std_time_graph(df):
    df_avg_std_delivers_by_city = round(
        df.loc[:, ["City", "Time_taken(min)"]]
        .groupby("City")
        .agg({"Time_taken(min)": ["mean", "std"]}),
        3,
    )
    df_avg_std_delivers_by_city.columns = [
        "avg_time_deliver",
        "std_time_deliver",
    ]
    df_avg_std_delivers_by_city = df_avg_std_delivers_by_city.reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Control",
            x=df_avg_std_delivers_by_city["City"],
            y=df_avg_std_delivers_by_city["avg_time_deliver"],
            error_y=dict(
                type="data",
                array=df_avg_std_delivers_by_city["std_time_deliver"],
            ),
        )
    )
    fig.update_layout(barmode="group")

    return fig


# Função Tempo médio e Desvio padrão de entrega por cidade e tipo de tráfego:
def avg_std_time_on_traffic(df):
    df_avg_std_delivers_by_city_and_traffic = round(
        df.loc[:, ["ID", "City", "Time_taken(min)", "Road_traffic_density"]]
        .groupby(["City", "Road_traffic_density"])
        .agg({"Time_taken(min)": ["mean", "std"]}),
        3,
    )
    df_avg_std_delivers_by_city_and_traffic.columns = [
        "avg_time_deliver",
        "std_time_deliver",
    ]
    df_avg_std_delivers_by_city_and_traffic = (
        df_avg_std_delivers_by_city_and_traffic.reset_index()
    )
    fig = px.sunburst(
        df_avg_std_delivers_by_city_and_traffic,
        path=["City", "Road_traffic_density"],
        values="avg_time_deliver",
        color="std_time_deliver",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=np.average(
            df_avg_std_delivers_by_city_and_traffic["std_time_deliver"]
        ),
    )

    return fig


# Função Distribuição da Distância:
def df_avg_std_delivers_by_city_and_typeorder(df):
    df_avg_std_delivers_by_city_and_typeorder = round(
        df.loc[:, ["ID", "City", "Time_taken(min)", "Type_of_order"]]
        .groupby(["City", "Type_of_order"])
        .agg({"Time_taken(min)": ["mean", "std"]}),
        3,
    )
    df_avg_std_delivers_by_city_and_typeorder.columns = [
        "avg_time_deliver",
        "std_time_deliver",
    ]
    df_avg_std_delivers_by_city_and_typeorder = (
        df_avg_std_delivers_by_city_and_typeorder.reset_index()
    )
    tabela_distancia = df_avg_std_delivers_by_city_and_typeorder
    return tabela_distancia


# --------------------------------------------- Início da Estrutura Lógica do Código ---------------------------------------------------------
# --------------------------------------
# Limpando os Dados chamando a função clean_code:
df = clean_code(df)
# --------------------------------------
# --------------------------------------

###############################################
# Sidebar no Streamlit:
###############################################

# Visão - Restaurantes:

st.header("Marketplace - Visão Restaurantes")

# image_path = "logo.jpg"
image = Image.open("logo.jpg")
st.sidebar.image(image, width=130)

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""___""")
st.sidebar.markdown("## Selecione uma data limite")
# date_slider = st.sidebar.slider(
#   "Até qual valor?",
#  value=pd.to_datetime(2022, 03, 13),
#  min_value=datetime.datetime(2022, 2, 11),
#  max_value=datetime.datetime(2022, 4, 6),
#  format="DD-MM-YYYY",
# )
# st.header(date_slider)
timestamp_min = pd.Timestamp(2022, 2, 11)
timestamp_max = pd.Timestamp(2022, 4, 13)
date_slider = st.sidebar.slider(
    "Selecione na barra:",
    min_value=timestamp_min.to_pydatetime(),
    max_value=timestamp_max.to_pydatetime(),
    value=(timestamp_max.to_pydatetime()),
    format="DD-MM-YYYY",
)

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    "Quais as condições do trânsito?",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"],
)


st.sidebar.markdown("""___""")

weather_options = st.sidebar.multiselect(
    "Quais as condições de clima?",
    ["Cloudy", "Fog", "Sandstorms", "Stormy", "Sunny", "Windy"],
    default=["Cloudy", "Fog", "Sandstorms", "Stormy", "Sunny", "Windy"],
)

st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS ")

# Ativar o Filtro nos Gráficos:

# Filtro de Data:
linhas_selecionadas = df["Order_Date"] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de Trânsito:
linhas_selecionadas = df["Road_traffic_density"].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

# Filtro de Clima:
linhas_selecionadas1 = df["Weatherconditions"].isin(weather_options)
df = df.loc[linhas_selecionadas1, :]
###############################################
# Layout no Streamlit:
###############################################

tab1, tab2, tab3 = st.tabs(["Visão Gerencial", " ", " "])

with tab1:
    with st.container():
        st.markdown("## Overall Metrics")

        col1, col2, col3, col4, col5, col6 = st.columns(6, gap="small")
        with col1:
            entregadores_unicos = df["Delivery_person_ID"].nunique()
            col1.metric("Entregadores Únicos", entregadores_unicos)

        with col2:
            # Cálculo da Distância entre restaurantes e dos locais de entrega:
            media_distancia = distance(df, fig=False)
            col2.metric("Distância Média(km)", media_distancia)

        with col3:
            df_festival = df.loc[df["Festival"] == "Yes", :]
            mean_time_festival = round(df_festival.loc[:, "Time_taken(min)"].mean(), 2)
            col3.metric("Tempo Médio de Entrega c/ Festival", mean_time_festival)

        with col4:
            df_festival = df.loc[df["Festival"] == "Yes", :]
            std_time_festival = round(df_festival.loc[:, "Time_taken(min)"].std(), 2)
            col4.metric("Desvio Padrão Médio de Entrega c/ Festival", std_time_festival)

        with col5:
            df_no_festival = df.loc[df["Festival"] == "No", :]
            mean_time_no_festival = round(
                df_no_festival.loc[:, "Time_taken(min)"].mean(), 2
            )
            col5.metric("Tempo Médio de Entrega s/ Festival", mean_time_no_festival)
        with col6:
            df_no_festival = df.loc[df["Festival"] == "No", :]
            std_time_no_festival = round(
                df_no_festival.loc[:, "Time_taken(min)"].std(), 2
            )
            col6.metric(
                "Desvio Padrão Médio de Entrega s/ Festival", std_time_no_festival
            )

    st.markdown("""___""")

    with st.container():
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.markdown("## Distribuição do Tempo")
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig)

        with col3:
            st.markdown("## Distribuição da Distância")
            tabela_distancia = df_avg_std_delivers_by_city_and_typeorder(df)
            st.dataframe(tabela_distancia)

st.markdown("""___""")

with st.container():
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("#### Tempo Médio de Entrega por Cidade")
        fig = distance(df, fig=True)
        st.plotly_chart(fig)

    with col3:
        st.markdown(
            "#### Tempo médio e Desvio padrão de entrega por cidade e tipo de tráfego"
        )
        fig = avg_std_time_on_traffic(df)
        st.plotly_chart(fig)
