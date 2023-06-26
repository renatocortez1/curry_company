import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", page_icon="👍")
# image_path = (
#    "C:/Users/corte/Desktop/Data Science/Repos/FTC_programacao_python/pagina_unica/")
image = Image.open("logo.jpg")
st.sidebar.image(image, width=130)

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""___""")

st.header("Curry Company Growth Dashboard")

st.markdown(
    """
  Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
  ### Como utilizar esse Growth Dashboard?
  - Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento.
    - Visão Tática: Indicadores semanais de crescimento.
    - Visão Geográfica: Insights de geolocalização.
  - Visão Entregador:
    - Acompanhamento dos indicadores semanais de crescimento.
  - Visão Restaurantes:
    - Indicadores semanais de crescimento dos restaurantes.
  ### Ask for Help:
  - Time de Data Sciente no Discord
  
  """
)
