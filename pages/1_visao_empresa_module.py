# Importando as bibliotecas:
import pandas as pd
import plotly.express as px
from haversine import haversine as hs
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

# --------------------------------------
# Importando o data set:
df_raw = pd.read_csv("train.csv")
df = df_raw.copy()

# Configurando a apresentação da Página:
st.set_page_config(page_title="Visão Empresa", page_icon="💸", layout="wide")

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


# Função order_metric:
def order_metric(df):
    cols = ["ID", "Order_Date"]
    # Seleção de Linhas
    df_aux = df.loc[:, cols].groupby("Order_Date").count().reset_index()

    # Desenhar o Gráfico de Linhas
    fig = px.bar(df_aux, x="Order_Date", y="ID")

    return fig


# Função traffic_order_share:
def traffic_order_share(df):
    df_aux = (
        df.loc[:, ["ID", "Road_traffic_density"]]
        .groupby("Road_traffic_density")
        .count()
        .reset_index()
    )
    # encontrando as porcentagens:
    df_aux["entregas_perc"] = df_aux["ID"] / df_aux["ID"].sum()
    fig = px.pie(df_aux, values="entregas_perc", names="Road_traffic_density")

    return fig


# Função traffic_order_city:
def traffic_order_city(df):
    df_aux = (
        df.loc[:, ["ID", "City", "Road_traffic_density"]]
        .groupby(["City", "Road_traffic_density"])
        .count()
        .reset_index()
    )
    fig = px.scatter(
        df_aux, x="City", y="Road_traffic_density", size="ID", color="City"
    )

    return fig


# Função order_by_week:
def order_by_week(df):
    # criar a coluna da semana:
    # - Começando no Domingo:
    df["week_of_year"] = df["Order_Date"].dt.strftime("%U")
    df_aux = (
        df.loc[:, ["ID", "week_of_year"]].groupby("week_of_year").count().reset_index()
    )

    fig = px.line(df_aux, x="week_of_year", y="ID")

    return fig


# Função order_share_by_week:
def order_share_by_week(df):
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux1 = (
        df.loc[:, ["ID", "week_of_year"]].groupby("week_of_year").count().reset_index()
    )
    df_aux2 = (
        df.loc[:, ["Delivery_person_ID", "week_of_year"]]
        .groupby("week_of_year")
        .nunique()
        .reset_index()
    )

    df_aux = pd.merge(df_aux1, df_aux2, how="inner")
    df_aux["order_by_deliver"] = df_aux["ID"] / df_aux["Delivery_person_ID"]

    fig = px.line(df_aux, x="week_of_year", y="order_by_deliver")

    return fig


# Função country_maps:
def country_maps(df):
    columns = [
        "City",
        "Road_traffic_density",
        "Delivery_location_latitude",
        "Delivery_location_longitude",
    ]

    columns_groupby = ["City", "Road_traffic_density"]
    data_plot = df.loc[:, columns].groupby(columns_groupby).median().reset_index()

    map_ = folium.Map(zoom_start=11)

    for index, location_info in data_plot.iterrows():
        folium.Marker(
            [
                location_info["Delivery_location_latitude"],
                location_info["Delivery_location_longitude"],
            ],
            popup=location_info[["City", "Road_traffic_density"]],
        ).add_to(map_)

    folium_static(map_, width=1024, height=600)


# --------------------------------------------- Início da Estrutura Lógica do Código ---------------------------------------------------------
# --------------------------------------
# Limpando os Dados chamando a função clean_code:
df = clean_code(df)
# --------------------------------------
# --------------------------------------
# Sidebar no Streamlit:
# --------------------------------------

# Visão - Empresa:

st.header("Marketplace - Visão Cliente")

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
st.sidebar.markdown("### Powered by Comunidade DS ")

# Ativar o Filtro nos Gráficos:

# Filtro de Data:
linhas_selecionadas = df["Order_Date"] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de Trânsito:
linhas_selecionadas = df["Road_traffic_density"].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

###############################################
# Layout no Streamlit:
###############################################

tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])

with tab1:
    with st.container():
        # Order Metric
        st.markdown("# Orders by Day")
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""___""")

    # Outro Container:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Traffic Order Share")
            fig = traffic_order_share(df)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Traffic Order City")
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.header("Order by Week")
        fig = order_by_week(df)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""___""")

    with st.container():
        st.header("Order Share by Week")
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Country Maps")
    country_maps(df)
