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
st.set_page_config(page_title="Visão Entregadores", page_icon="🚚", layout="wide")
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


# Função top_delivers_fast:
def top_delivers(df, top_asc):
    entregadores_rapidos = round(
        df.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"]]
        .groupby(["City", "Delivery_person_ID"])
        .mean()
        .sort_values(["City", "Time_taken(min)"], ascending=top_asc)
        .reset_index(),
        2,
    )
    df_aux01 = entregadores_rapidos.loc[
        entregadores_rapidos["City"] == "Metropolitian", :
    ].head(10)
    df_aux02 = entregadores_rapidos.loc[
        entregadores_rapidos["City"] == "Urban", :
    ].head(10)
    df_aux03 = entregadores_rapidos.loc[
        entregadores_rapidos["City"] == "Semi-Urban", :
    ].head(10)

    df_final1 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df_final1


# --------------------------------------------- Início da Estrutura Lógica do Código ---------------------------------------------------------
# --------------------------------------
# Limpando os Dados chamando a função clean_code:
df = clean_code(df)
# --------------------------------------
# --------------------------------------
###############################################
# Sidebar no Streamlit:
###############################################

# Visão - Entregadores:

st.header("Marketplace - Visão Entregadores")

#image_path = "logo.jpg"
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
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap="large")
        with col1:
            st.subheader("Maior Idade")
            maior_idade = df.loc[:, "Delivery_person_Age"].max()
            col1.metric("Anos", maior_idade)

        with col2:
            st.subheader("Menor Idade")
            menor_idade = df.loc[:, "Delivery_person_Age"].min()
            col2.metric("Anos", menor_idade)

        with col3:
            st.subheader("Melhor Condição")
            melhor_condicao = df.loc[:, "Vehicle_condition"].max()
            col3.metric("Condição de Veículo", melhor_condicao)
        with col4:
            st.subheader("Pior Condição ")
            pior_condicao = df.loc[:, "Vehicle_condition"].min()
            col4.metric("Condição de Veículo", pior_condicao)

    with st.container():
        st.markdown("""___""")
        st.subheader("Avaliações")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Avaliações Médias por Entregador")
            avaliacao_por_entregador = round(
                df.loc[:, ["Delivery_person_Ratings", "Delivery_person_ID"]]
                .groupby("Delivery_person_ID")
                .mean()
                .reset_index(),
                2,
            )
            st.dataframe(avaliacao_por_entregador)

        with col2:
            st.markdown("##### Avaliações Médias por Trânsito")
            # Juntar os comandos em uma só linha de código:
            avaliacao_por_transito = round(
                (
                    df.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]]
                    .groupby("Road_traffic_density")
                    .agg({"Delivery_person_Ratings": ["mean", "std"]})
                ),
                2,
            )
            # Mudança de nome das colunas:
            avaliacao_por_transito.columns = ["delivery_mean", "delivery_std"]
            # Reset do Index:
            avaliacao_por_transito = avaliacao_por_transito.reset_index()
            st.dataframe(avaliacao_por_transito)

            st.markdown("##### Avaliações Médias por Clima")
            # Juntar os comandos em uma só linha de código:
            avaliacao_por_clima = round(
                df.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]]
                .groupby("Weatherconditions")
                .agg({"Delivery_person_Ratings": ["mean", "std"]}),
                2,
            )
            # Mudança no nome das colunas:
            avaliacao_por_clima.columns = ["delivery_mean", "delivery_std"]
            # Reset do Index:
            avaliacao_por_clima = avaliacao_por_clima.reset_index()
            st.dataframe(avaliacao_por_clima)

    with st.container():
        st.markdown("""___""")
        st.title("Velocidade de Entrega")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Top 10 Entregadores mais rápidos")
            df_final1 = top_delivers(df, top_asc=True)
            st.dataframe(df_final1)

        with col2:
            st.markdown("##### Top 10 Entregadores mais lentos")
            df_final2 = top_delivers(df, top_asc=False)
            st.dataframe(df_final2)
