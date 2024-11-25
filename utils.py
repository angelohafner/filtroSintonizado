
# Definição do nome do arquivo de parâmetros
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

from matplotlib.ticker import EngFormatter

import numpy as np
# Função para formatar os resultados
def format_results(Z_R, Z_L, Z_C, Z_F, I_R, I_L, I_C, I_F, V_R, V_L, V_C,
                   total_cap_count, nominal_cell_voltage, nominal_cell_power, 
                   nominal_cell_capacitance, bank_capacitance, short_circuit_inductor_current,
                   L_mH, r, inductor_overcurrent):
    formatter = EngFormatter(unit='')
    V_sum = V_R + V_L + V_C
    def format_with_unit(value, unit):
        return f"{formatter.format_eng(value)}{unit}"

    results = {
        "Impedance (ohm)": {
            "Resistor":  f"({np.abs(Z_R):.2f} ∠ {np.angle(Z_R, deg=True):.2f}°) Ω",
            "Inductor":  f"({np.abs(Z_L):.2f} ∠ {np.angle(Z_L, deg=True):.2f}°) Ω",
            "Capacitor": f"({np.abs(Z_C):.2f} ∠ {np.angle(Z_C, deg=True):.2f}°) Ω",
            "Filter":    f"({np.abs(Z_F):.2f} ∠ {np.angle(Z_F, deg=True):.2f}°) Ω"
        },
        "Current (A)": {
            "Resistor":  f"({np.abs(I_R):.2f} ∠ {np.angle(I_R, deg=True):.2f}°) A",
            "Inductor":  f"({np.abs(I_L):.2f} ∠ {np.angle(I_L, deg=True):.2f}°) A",
            "Capacitor": f"({np.abs(I_C):.2f} ∠ {np.angle(I_C, deg=True):.2f}°) A",
            "Filter":    f"({np.abs(I_F):.2f} ∠ {np.angle(I_F, deg=True):.2f}°) A"
        },
        "Voltage (V)": {
            "Resistor":  f"({np.abs(V_R):.2f} ∠ {np.angle(V_R, deg=True):.2f}°) V",
            "Inductor":  f"({np.abs(V_L):.2f} ∠ {np.angle(V_L, deg=True):.2f}°) V",
            "Capacitor": f"({np.abs(V_C):.2f} ∠ {np.angle(V_C, deg=True):.2f}°) V",
            "Capac_pu":  f"({np.abs(V_C)/np.abs(V_sum):.2f}) pu",
        },
        "Three-phase Power (kVA)": {
            "Resistor":  f"({3e-3 * np.abs(V_R) * np.abs(I_R):.2f} ∠ {np.angle(V_R, deg=True)-np.angle(I_R, deg=True):.2f}°) kW",
            "Inductor":  f"({3e-3 * np.abs(V_L) * np.abs(I_L):.2f} ∠ {np.angle(V_L, deg=True)-np.angle(I_L, deg=True):.2f}°) kVAr",
            "Capacitor": f"({3e-3 * np.abs(V_C) * np.abs(I_C):.2f} ∠ {np.angle(V_C, deg=True)-np.angle(I_C, deg=True):.2f}°) kVAr",
            "Filter":    f"({3e-3 * np.abs(V_sum) * np.abs(I_C):.2f} ∠ {np.angle(V_sum, deg=True) - np.angle(I_C, deg=True):.2f}°) kVA",
        },
        "Capacitor Cells": {
            "Total Number of Cells":    f"{total_cap_count:.0f}",
            "Nominal Cell Voltage":     format_with_unit(nominal_cell_voltage, "V"),
            "Nominal Cell Power":       format_with_unit(nominal_cell_power, "VAR"),
            "Nominal Cell Capacitance": format_with_unit(nominal_cell_capacitance, "F"),
            "Bank Capacitance":         format_with_unit(bank_capacitance, "F")
        },
        "Inductor": {
            "Short-Circuit Current":  format_with_unit(short_circuit_inductor_current, "A"),
            "Inductance":             format_with_unit(L_mH / 1000, "H"),
            "Inductor Resistance":    format_with_unit(r, "Ω"),
            "Inductor Rated Current": format_with_unit(inductor_overcurrent * np.abs(I_L), "A"),
        }
    }
    return results


import io
import json
import pandas as pd

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
