import math
from decimal import Decimal, getcontext
import pandas as pd  # Importamos pandas para trabajar con tablas (DataFrames)
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# Configurar la precisión deseada para Decimal
getcontext().prec = 100

# Función para convertir de DMS a grados decimales usando Decimal
def dms_a_grados(grados, minutos, segundos):
    grados_decimal = Decimal(grados)
    minutos_decimal = Decimal(minutos) / Decimal(60)
    segundos_decimal = Decimal(segundos) / Decimal(3600)
    return grados_decimal + minutos_decimal + segundos_decimal

# Función para convertir de grados decimales a DMS usando Decimal
def grados_a_dms(grados_decimales, decimales=6):
    grados = int(grados_decimales)
    minutos_decimales = (Decimal(grados_decimales) - Decimal(grados)) * Decimal(60)
    minutos = abs(int(minutos_decimales))
    segundos = abs((minutos_decimales - Decimal(minutos)) * Decimal(60))
    return f"{grados}°{minutos}'{round(segundos, decimales)}''"

class AnguloApp(App):
    def build(self):
        self.layout = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scrollview = ScrollView(size_hint=(1, None), size=(400, 600))
        self.scrollview.add_widget(self.layout)

        # Inputs para los vértices
        self.layout.add_widget(Label(text="Número de vértices:"))
        self.n_vertices_input = TextInput(multiline=False)
        self.layout.add_widget(self.n_vertices_input)

        self.layout.add_widget(Label(text="Instrumento:"))
        self.instrumento_input = TextInput(multiline=False)
        self.layout.add_widget(self.instrumento_input)

        self.layout.add_widget(Label(text="Precisión (en segundos):"))
        self.precision_input = TextInput(multiline=False)
        self.layout.add_widget(self.precision_input)

        # Botón para agregar vértices
        self.add_vertex_button = Button(text="Agregar vértices", on_press=self.add_vertex_fields)
        self.layout.add_widget(self.add_vertex_button)

        # Botón para calcular
        self.calculate_button = Button(text="Calcular", on_press=self.calcular_resultado)
        self.layout.add_widget(self.calculate_button)

        # Output
        self.output_label = Label(text="Resultados:")
        self.layout.add_widget(self.output_label)
        self.result_label = Label(text="", size_hint_y=None)
        self.layout.add_widget(self.result_label)

        return self.scrollview

    def add_vertex_fields(self, instance):
        n_vertices = int(self.n_vertices_input.text)

        # Agregar campos para cada vértice
        self.angulos_inputs = []
        for i in range(n_vertices):
            self.layout.add_widget(Label(text=f"Punto {i+1} (grados):"))
            grados_input = TextInput(multiline=False)
            self.layout.add_widget(grados_input)

            self.layout.add_widget(Label(text=f"Punto {i+1} (minutos):"))
            minutos_input = TextInput(multiline=False)
            self.layout.add_widget(minutos_input)

            self.layout.add_widget(Label(text=f"Punto {i+1} (segundos):"))
            segundos_input = TextInput(multiline=False)
            self.layout.add_widget(segundos_input)

            self.angulos_inputs.append((grados_input, minutos_input, segundos_input))

    def calcular_resultado(self, instance):
        # Obtener valores de la interfaz
        n_vertices = int(self.n_vertices_input.text)
        instrumento = self.instrumento_input.text
        precision = Decimal(self.precision_input.text)

        angulos_campo = {}
        for i, (grados_input, minutos_input, segundos_input) in enumerate(self.angulos_inputs):
            grados = int(grados_input.text)
            minutos = int(minutos_input.text)
            segundos = Decimal(segundos_input.text)
            angulos_campo[f"Punto {i+1}"] = (grados, minutos, segundos)

        # Convertir los ángulos a grados decimales
        angulos_decimales = {punto: dms_a_grados(*dms) for punto, dms in angulos_campo.items()}

        # Calcular la suma teórica
        suma_teorica = (Decimal(n_vertices) - Decimal(2)) * Decimal(180)

        # Calcular la suma medida
        suma_medida = sum(angulos_decimales.values())

        # Error máximo permitido
        precision_grados = precision / Decimal(3600)
        EMP = precision_grados * Decimal(math.sqrt(n_vertices))

        # Diferencia entre suma teórica y suma medida
        diferencia = abs(suma_teorica - suma_medida)

        # Convertir a DMS para mostrar
        diferencia_dms = grados_a_dms(diferencia)
        EMP_dms = grados_a_dms(EMP)
        suma_medida_dms = grados_a_dms(suma_medida)

        # Mostrar resultados
        self.result_label.text = f"Suma medida: {suma_medida_dms}\n" \
                                 f"Error de cierre: {diferencia_dms}\n" \
                                 f"Error máximo permitido: {EMP_dms}\n"

class AnguloApp(App):
    def build(self):
        return AnguloApp()

if __name__ == "__main__":
    AnguloApp().run()
