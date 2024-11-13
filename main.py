import streamlit as st
import openpyxl
import numpy as np
import pandas as pd
import json
import os
import io
from matplotlib.ticker import EngFormatter
import chardet

# Arquivo de parâmetros padrão para download
PARAMETERS_FILE = "parameters.txt"

# Função para criar o arquivo de parâmetros padrão
def create_default_parameters():
    with open(PARAMETERS_FILE, "w") as file:
        file.write(
            """# Frequência fundamental em Hz
f1 = 60

# Resistência em ohms do indutor
r = 2.849

# Indutância do indutor em miliHenries (mH)
L_mH = 204.949

# Capacitância do capacitor em microFarads (uF)
C_uF = 3.945

# Tensão de linha em kV (quilovolts)
V_line_kV = 34.5

# Sobretensão permitida nos capacitores (fator de multiplicação)
capacitor_overvoltage = 1.3

# Sobrecorrente permitida no indutor (fator de multiplicação)
inductor_overcurrent = 1.66

# Número de capacitores em série
series_cap_count = 2

# Número de capacitores em paralelo
parallel_cap_count = 1
"""
        )

# Função para carregar parâmetros
def load_parameters(uploaded_file):
    parameters = {}
    try:
        file_content = uploaded_file.read().decode("utf-8").splitlines()
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        file_content = uploaded_file.read().decode("ISO-8859-1").splitlines()

    for line in file_content:
        if line.strip() and not line.startswith("#"):
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()
            parameters[key] = float(value) if '.' in value else int(value)
    return parameters

# Função principal de cálculo do filtro sintonizado
def calcular_filtro_sintonizado(f1, r, L_mH, C_uF, V_line_kV, capacitor_overvoltage, inductor_overcurrent, series_cap_count, parallel_cap_count):
    w1 = 2 * np.pi * f1

    def calcular_impedancia(r, L, C, w):
        Z_R = complex(r, 0)
        Z_L = complex(0, w * L * 1e-3)
        Z_C = complex(0, -1 / (w * C * 1e-6))
        Z_F = Z_R + Z_L + Z_C
        return Z_R, Z_L, Z_C, Z_F

    def calcular_corrente_tensao(V_linha, Z_R, Z_L, Z_C, Z_F):
        V_fase = V_linha * 1e3 / np.sqrt(3)
        I_R = I_L = I_C = I_F = V_fase / Z_F
        V_R, V_L, V_C = I_R * Z_R, I_L * Z_L, I_C * Z_C
        return I_R, I_L, I_C, I_F, V_R, V_L, V_C

    def detalhes_capacitor(V_C, P_C):
        total_cap_count = 3 * series_cap_count * parallel_cap_count
        nominal_cell_voltage = np.abs(V_C) * capacitor_overvoltage / series_cap_count
        nominal_cell_power = 3 * np.abs(P_C) * capacitor_overvoltage ** 2 / total_cap_count
        nominal_cell_capacitance = 1 / (w1 * nominal_cell_voltage ** 2 / nominal_cell_power)
        bank_capacitance = nominal_cell_capacitance * parallel_cap_count / series_cap_count
        return total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance

    def corrente_curto(V_line_kV, L_mH, f1):
        L_h = L_mH * 1e-3
        V_fase = V_line_kV * 1e3 / np.sqrt(3)
        X_L = 2 * np.pi * f1 * L_h
        return V_fase / X_L

    Z_R, Z_L, Z_C, Z_F = calcular_impedancia(r, L_mH, C_uF, w1)
    I_R, I_L, I_C, I_F, V_R, V_L, V_C = calcular_corrente_tensao(V_line_kV, Z_R, Z_L, Z_C, Z_F)
    total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance = detalhes_capacitor(V_C, V_C * np.conj(I_C))
    short_circuit_inductor_current = corrente_curto(V_line_kV, L_mH, f1)

    return Z_R, Z_L, Z_C, Z_F, I_R, I_L, I_C, I_F, V_R, V_L, V_C, total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance, short_circuit_inductor_current, L_mH, r

# Formatação de resultados
def format_results(Z_R, Z_L, Z_C, Z_F, I_R, I_L, I_C, I_F, V_R, V_L, V_C, total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance, short_circuit_inductor_current, L_mH, r):
    formatter = EngFormatter(unit='')

    def format_with_unit(value, unit):
        return f"{formatter.format_eng(value)}{unit}"

    results = {
        "Impedance (ohm)": {
            "Resistor": f"({np.abs(Z_R):.2f} ∠ {np.angle(Z_R, deg=True):.2f}°) Ω",
            "Inductor": f"({np.abs(Z_L):.2f} ∠ {np.angle(Z_L, deg=True):.2f}°) Ω",
            "Capacitor": f"({np.abs(Z_C):.2f} ∠ {np.angle(Z_C, deg=True):.2f}°) Ω",
            "Filter": f"({np.abs(Z_F):.2f} ∠ {np.angle(Z_F, deg=True):.2f}°) Ω"
        },
        "Current (A)": {
            "Resistor": f"({np.abs(I_R):.2f} ∠ {np.angle(I_R, deg=True):.2f}°) A",
            "Inductor": f"({np.abs(I_L):.2f} ∠ {np.angle(I_L, deg=True):.2f}°) A",
            "Capacitor": f"({np.abs(I_C):.2f} ∠ {np.angle(I_C, deg=True):.2f}°) A",
            "Filter": f"({np.abs(I_F):.2f} ∠ {np.angle(I_F, deg=True):.2f}°) A"
        },
        "Voltage (V)": {
            "Resistor": f"({np.abs(V_R):.2f} ∠ {np.angle(V_R, deg=True):.2f}°) V",
            "Inductor": f"({np.abs(V_L):.2f} ∠ {np.angle(V_L, deg=True):.2f}°) V",
            "Capacitor": f"({np.abs(V_C):.2f} ∠ {np.angle(V_C, deg=True):.2f}°) V",
        },
        "Capacitor Cells": {
            "Total Number of Cells": f"{total_cap_count:.0f}",
            "Nominal Cell Voltage": format_with_unit(nominal_cell_voltage, "V"),
            "Nominal Cell Power": format_with_unit(nominal_cell_power, "VAR"),
            "Nominal Cell Capacitance": format_with_unit(nominal_cell_capacitance, "F"),
            "Bank Capacitance": format_with_unit(bank_capacitance, "F")
        },
        "Inductor": {
            "Short-Circuit Current": format_with_unit(short_circuit_inductor_current, "A"),
            "Inductance": format_with_unit(L_mH / 1000, "H"),
            "Inductor Resistance": format_with_unit(r, "Ω")
        }
    }
    return results


# Função para salvar os resultados em TXT, JSON e XLSX
def save_results_as_files(results):
    # Salvar em JSON
    json_file = io.StringIO()
    json.dump(results, json_file, indent=4)
    json_file = io.BytesIO(json_file.getvalue().encode("utf-8"))  # Converter para BytesIO para o download

    # Salvar em TXT
    txt_file = io.StringIO()
    txt_content = "\n".join([f"{section}:\n" + "\n".join([f"{k}: {v}" for k, v in data.items()]) for section, data in results.items()])
    txt_file.write(txt_content)
    txt_file = io.BytesIO(txt_file.getvalue().encode("utf-8"))

    # Salvar em XLSX
    xlsx_file = io.BytesIO()
    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        for sheet_name, data in results.items():
            df = pd.DataFrame(data.items(), columns=["Parameter", "Value"])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    xlsx_file.seek(0)

    return json_file, txt_file, xlsx_file


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
    results = calcular_filtro_sintonizado(
        params["f1"], params["r"], params["L_mH"], params["C_uF"],
        params["V_line_kV"], params["capacitor_overvoltage"],
        params["inductor_overcurrent"], params["series_cap_count"], params["parallel_cap_count"]
    )
    formatted_results = format_results(*results)
    st.subheader("Resultados:")
    st.json(formatted_results)

    # Chamar a função para salvar os resultados
    json_file, txt_file, xlsx_file = save_results_as_files(formatted_results)

    # Botões de download
    st.download_button(label="Baixar results.json", data=json_file, file_name="results.json")
    st.download_button(label="Baixar results.txt", data=txt_file, file_name="results.txt")
    st.download_button(label="Baixar results.xlsx", data=xlsx_file, file_name="results.xlsx")
