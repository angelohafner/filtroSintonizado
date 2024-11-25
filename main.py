# Importação da classe FiltroSintonizado
from filtro_sintonizado import FiltroSintonizado
import streamlit as st
from utils import *




# Interface do Streamlit
st.title("Simulação de Filtro Sintonizado")

# Download do arquivo parameters.txt
st.header("1. Baixe o arquivo de parâmetros")
create_default_parameters()
with open(PARAMETERS_FILE, "rb") as file:
    st.download_button(label="Baixar parameters.txt", data=file, file_name="parameters.txt")

# Upload do arquivo parameters.txt após edição
st.header("2. Faça o upload do arquivo parameters.txt editado")
uploaded_file = st.file_uploader("Carregue o arquivo parameters.txt editado", type="txt")

# Gerar os arquivos e adicionar os botões de download após os resultados
if uploaded_file:
    params = load_parameters(uploaded_file)

    # Instanciar a classe com os parâmetros carregados
    filtro = FiltroSintonizado(
        f1=params["f1"],
        r=params["r"],
        L_mH=params["L_mH"],
        C_uF=params["C_uF"],
        V_line_kV=params["V_line_kV"],
        capacitor_overvoltage=params["capacitor_overvoltage"],
        inductor_overcurrent=params["inductor_overcurrent"],
        series_cap_count=params["series_cap_count"],
        parallel_cap_count=params["parallel_cap_count"]
    )

    # Executar o cálculo usando a classe
    resultados = filtro.calcular()

    # Formatar os resultados para exibição
    formatted_results = format_results(**resultados)
    st.subheader("Resultados:")
    st.json(formatted_results)

    # Salvar os resultados em arquivos
    json_file, txt_file, xlsx_file = save_results_as_files(formatted_results)

    # Botões de download
    st.download_button(label="Baixar results.json", data=json_file, file_name="results.json")
    st.download_button(label="Baixar results.txt", data=txt_file, file_name="results.txt")
    st.download_button(label="Baixar results.xlsx", data=xlsx_file, file_name="results.xlsx")
