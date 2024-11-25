import numpy as np

class FiltroSintonizado:
    def __init__(self, f1, r, L_mH, C_uF, V_line_kV, capacitor_overvoltage, inductor_overcurrent, series_cap_count, parallel_cap_count):
        self.f1 = f1
        self.r = r
        self.L_mH = L_mH
        self.C_uF = C_uF
        self.V_line_kV = V_line_kV
        self.capacitor_overvoltage = capacitor_overvoltage
        self.inductor_overcurrent = inductor_overcurrent
        self.series_cap_count = series_cap_count
        self.parallel_cap_count = parallel_cap_count
        self.w1 = 2 * np.pi * f1

    def calcular_impedancia(self):
        # Calcula as impedâncias do filtro
        Z_R = complex(self.r, 0)
        Z_L = complex(0, self.w1 * self.L_mH * 1e-3)
        Z_C = complex(0, -1 / (self.w1 * self.C_uF * 1e-6))
        Z_F = Z_R + Z_L + Z_C
        return Z_R, Z_L, Z_C, Z_F

    def calcular_corrente_tensao(self, Z_R, Z_L, Z_C, Z_F):
        # Calcula as correntes e tensões no circuito
        V_fase = self.V_line_kV * 1e3 / np.sqrt(3)
        I_R = I_L = I_C = I_F = V_fase / Z_F
        V_R, V_L, V_C = I_R * Z_R, I_L * Z_L, I_C * Z_C
        return I_R, I_L, I_C, I_F, V_R, V_L, V_C

    def detalhes_capacitor(self, V_C, P_C):
        # Calcula os detalhes do capacitor
        total_cap_count = 3 * self.series_cap_count * self.parallel_cap_count
        nominal_cell_voltage = np.abs(V_C) * self.capacitor_overvoltage / self.series_cap_count
        nominal_cell_power = 3 * np.abs(P_C) * self.capacitor_overvoltage ** 2 / total_cap_count
        nominal_cell_capacitance = 1 / (self.w1 * nominal_cell_voltage ** 2 / nominal_cell_power)
        bank_capacitance = nominal_cell_capacitance * self.parallel_cap_count / self.series_cap_count
        return total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance

    def corrente_curto(self):
        # Calcula a corrente de curto-circuito no indutor
        L_h = self.L_mH * 1e-3
        V_fase = self.V_line_kV * 1e3 / np.sqrt(3)
        X_L = 2 * np.pi * self.f1 * L_h
        return V_fase / X_L

    def calcular(self):
        # Executa os cálculos principais do filtro sintonizado
        Z_R, Z_L, Z_C, Z_F = self.calcular_impedancia()
        I_R, I_L, I_C, I_F, V_R, V_L, V_C = self.calcular_corrente_tensao(Z_R, Z_L, Z_C, Z_F)
        total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, bank_capacitance = self.detalhes_capacitor(
            V_C, V_C * np.conj(I_C)
        )
        short_circuit_inductor_current = self.corrente_curto()

        return {
            "Z_R": Z_R,
            "Z_L": Z_L,
            "Z_C": Z_C,
            "Z_F": Z_F,
            "I_R": I_R,
            "I_L": I_L,
            "I_C": I_C,
            "I_F": I_F,
            "V_R": V_R,
            "V_L": V_L,
            "V_C": V_C,
            "total_cap_count": total_cap_count,
            "nominal_cell_voltage": nominal_cell_voltage,
            "nominal_cell_power": nominal_cell_power,
            "nominal_cell_capacitance": nominal_cell_capacitance,
            "bank_capacitance": bank_capacitance,
            "short_circuit_inductor_current": short_circuit_inductor_current,
            "L_mH": self.L_mH,
            "r": self.r,
            "inductor_overcurrent": self.inductor_overcurrent
        }
