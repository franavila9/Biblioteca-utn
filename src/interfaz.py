import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
from tksheet import Sheet

from simulador import SimuladorBiblioteca
from parametros import PARAMETROS_DEFAULT
from exportador import exportar_a_excel
from validaciones import (
    validar_parametros,
    convertir_valor,
    es_texto_decimal_valido,
    es_texto_entero_valido,
    CAMPOS_ENTEROS,
)


class InterfazBiblioteca:
    def __init__(self, root):
        self.root = root
        self.root.title("TP4 - Simulación Biblioteca UTN")
        self.root.geometry("1500x800")

        self.df_vector_completo = pd.DataFrame()
        self.df_vector_mostrado = pd.DataFrame()
        self.ultimo_resultado = {}
        self.entries = {}

        self.crear_widgets()

    def crear_widgets(self):
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill="both", expand=True)

        frame_parametros = ttk.LabelFrame(frame_principal, text="Parámetros")
        frame_parametros.pack(fill="x", padx=10, pady=10)

        self.crear_inputs_parametros(frame_parametros)

        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(fill="x", padx=10, pady=5)

        self.btn_simular = ttk.Button(
            frame_botones,
            text="Ejecutar simulación",
            command=self.ejecutar_simulacion
        )
        self.btn_simular.pack(side="left", padx=5)

        self.btn_exportar = ttk.Button(
            frame_botones,
            text="Exportar a Excel",
            command=self.exportar_excel
        )
        self.btn_exportar.pack(side="left", padx=5)

        frame_resultados = ttk.LabelFrame(frame_principal, text="Resultados")
        frame_resultados.pack(fill="x", padx=10, pady=5)

        self.lbl_resultados = ttk.Label(
            frame_resultados,
            text="Todavía no se ejecutó ninguna simulación."
        )
        self.lbl_resultados.pack(anchor="w", padx=10, pady=10)

        frame_tabla = ttk.LabelFrame(frame_principal, text="Vector de estado")
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.sheet = Sheet(
            frame_tabla,
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            width=1450,
            height=430
        )

        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_select",
            "drag_select",
            "arrowkeys",
            "right_click_popup_menu",
            "rc_select",
            "copy",
        )

        self.sheet.pack(fill="both", expand=True)

    def crear_inputs_parametros(self, frame):
        campos = [
            ("tiempo_maximo", "Tiempo máximo X"),
            ("hora_desde", "Hora desde j"),
            ("cantidad_iteraciones_mostrar", "Iteraciones i"),
            ("tiempo_entre_llegadas", "Tiempo entre llegadas"),

            ("prob_prestamo", "Prob. préstamo"),
            ("prob_devolucion", "Prob. devolución"),
            ("prob_consulta", "Prob. consulta"),
            ("consulta_min", "Consulta mín."),

            ("consulta_max", "Consulta máx."),
            ("media_prestamo", "Media préstamo"),
            ("devolucion_min", "Devolución mín."),
            ("devolucion_max", "Devolución máx."),

            ("prob_se_retira", "Prob. se retira"),
            ("prob_lee_en_sala", "Prob. lee en sala"),
            ("media_lectura", "Media lectura"),
            ("capacidad_maxima", "Capacidad máxima"),

            ("max_iteraciones", "Máx. iteraciones"),
        ]

        validacion_decimal = self.root.register(es_texto_decimal_valido)
        validacion_entera = self.root.register(es_texto_entero_valido)

        columnas_por_fila = 4

        for index, (clave, etiqueta) in enumerate(campos):
            fila = index // columnas_por_fila
            columna_base = (index % columnas_por_fila) * 2

            ttk.Label(frame, text=etiqueta).grid(
                row=fila,
                column=columna_base,
                padx=5,
                pady=4,
                sticky="w"
            )

            if clave in CAMPOS_ENTEROS:
                entry = ttk.Entry(
                    frame,
                    width=12,
                    validate="key",
                    validatecommand=(validacion_entera, "%P")
                )
            else:
                entry = ttk.Entry(
                    frame,
                    width=12,
                    validate="key",
                    validatecommand=(validacion_decimal, "%P")
                )

            entry.grid(
                row=fila,
                column=columna_base + 1,
                padx=5,
                pady=4,
                sticky="w"
            )

            entry.insert(0, str(PARAMETROS_DEFAULT[clave]))
            self.entries[clave] = entry

    def leer_parametros(self):
        parametros = {}

        for clave, entry in self.entries.items():
            valor = entry.get()
            parametros[clave] = convertir_valor(clave, valor)

        validar_parametros(parametros)

        return parametros

    def ejecutar_simulacion(self):
        try:
            parametros = self.leer_parametros()

            self.btn_simular.config(state="disabled")
            self.btn_exportar.config(state="disabled")
            self.lbl_resultados.config(text="Simulando, por favor esperá...")
            self.root.update_idletasks()

            simulador = SimuladorBiblioteca(parametros=parametros)
            vector_estado = simulador.simular()

            self.df_vector_mostrado = pd.DataFrame(vector_estado).fillna("-")
            self.df_vector_completo = self.df_vector_mostrado.copy()

            self.ultimo_resultado = self.calcular_resultados(simulador, parametros)

            self.cargar_tabla(self.df_vector_mostrado)
            self.mostrar_resultados(self.ultimo_resultado)

            self.btn_simular.config(state="normal")
            self.btn_exportar.config(state="normal")

        except ValueError as error:
            self.btn_simular.config(state="normal")
            self.btn_exportar.config(state="normal")
            messagebox.showerror("Error de parámetros", str(error))

        except Exception as error:
            self.btn_simular.config(state="normal")
            self.btn_exportar.config(state="normal")
            messagebox.showerror("Error inesperado", str(error))

    def calcular_resultados(self, simulador, parametros):
        promedio_permanencia = 0.0
        if simulador.contador_clientes_salieron > 0:
            promedio_permanencia = simulador.acum_tiempo_permanencia / simulador.contador_clientes_salieron

        tiempo_total = parametros["tiempo_maximo"]

        porcentaje_ocio_emp_1 = 0
        porcentaje_ocio_emp_2 = 0

        if tiempo_total > 0:
            porcentaje_ocio_emp_1 = (
                simulador.empleado_1.tiempo_ocioso_acumulado / tiempo_total * 100
            )
            porcentaje_ocio_emp_2 = (
                simulador.empleado_2.tiempo_ocioso_acumulado / tiempo_total * 100
            )

        return {
            "promedio_permanencia": round(promedio_permanencia, 2),
            "tiempo_ocioso_empleado_1": round(
                simulador.empleado_1.tiempo_ocioso_acumulado,
                2
            ),
            "tiempo_ocioso_empleado_2": round(
                simulador.empleado_2.tiempo_ocioso_acumulado,
                2
            ),
            "porcentaje_ocio_empleado_1": round(porcentaje_ocio_emp_1, 2),
            "porcentaje_ocio_empleado_2": round(porcentaje_ocio_emp_2, 2),
        }

    def cargar_tabla(self, df):
        if df.empty:
            self.sheet.set_sheet_data([])
            self.sheet.headers([])
            return

        df = df.fillna("-")

        columnas = list(df.columns)
        datos = df.astype(str).values.tolist()

        self.sheet.set_sheet_data(datos)
        self.sheet.headers(columnas)

        for indice, columna in enumerate(columnas):
            ancho = self.obtener_ancho_columna(columna)
            self.sheet.column_width(column=indice, width=ancho)

        self.aplicar_colores_columnas(columnas)

        self.sheet.refresh()

    def obtener_ancho_columna(self, columna):
        anchos = {
            "fila": 60,
            "evento": 240,
            "reloj": 75,

            "rnd_tipo_tramite": 125,
            "tipo_tramite": 115,
            "tiempo_entre_llegadas": 155,
            "proxima_llegada": 135,

            "rnd_atencion": 120,
            "tiempo_atencion": 135,
            "fin_atencion(1)": 135,
            "fin_atencion(2)": 135,

            "rnd_post_prestamo": 150,
            "post_prestamo": 130,
            "rnd_tiempo_lectura": 160,
            "tiempo_lectura": 135,
            "proximo_fin_lectura": 160,

            "empleado(1)_estado": 170,
            "empleado(2)_estado": 170,
            "cola": 70,

            "cantidad_personas": 145,
            "estado_biblioteca": 145,

            "tiempo_transcurrido": 210,
            "cant_personas_promedio": 210,
            "promedio_permanencia": 220,
            "ac_ocio_empleado_1": 190,
            "ac_ocio_empleado_2": 190,
        }

        if columna.startswith("cli("):
            return 145

        return anchos.get(columna, 125)

    def aplicar_colores_columnas(self, columnas):
        for indice, columna in enumerate(columnas):
            color = "#FFFFFF"

            if columna in ["fila", "evento", "reloj"]:
                color = "#EDEDED"

            elif columna in [
                "rnd_tipo_tramite",
                "tipo_tramite",
                "tiempo_entre_llegadas",
                "proxima_llegada",
            ]:
                color = "#D9EAF7"

            elif columna in [
                "rnd_atencion",
                "tiempo_atencion",
                "fin_atencion(1)",
                "fin_atencion(2)",
            ]:
                color = "#FFF2CC"

            elif columna in [
                "rnd_post_prestamo",
                "post_prestamo",
                "rnd_tiempo_lectura",
                "tiempo_lectura",
                "proximo_fin_lectura",
            ]:
                color = "#C6EFCE"

            elif columna in [
                "empleado(1)_estado",
                "empleado(2)_estado",
                "cola",
                "cantidad_personas",
                "estado_biblioteca",
            ]:
                color = "#DDEBF7"

            elif columna in [
                "acum_tiempo_permanencia",
                "contador_clientes_salieron",
                "tiempo_promedio_permanencia",
                "ac_ocio_empleado_1",
                "ac_ocio_empleado_2",
            ]:
                color = "#FCE4D6"

            elif columna.startswith("cli("):
                color = "#D9EAD3"

            self.sheet.highlight_columns(
                columns=[indice],
                bg=color,
                fg="black",
                redraw=False
            )

    def mostrar_resultados(self, resultados):
        texto = (
            f"Promedio permanencia: {resultados['promedio_permanencia']} min | "
            f"Ocio Emp. 1: {resultados['tiempo_ocioso_empleado_1']} min "
            f"({resultados['porcentaje_ocio_empleado_1']}%) | "
            f"Ocio Emp. 2: {resultados['tiempo_ocioso_empleado_2']} min "
            f"({resultados['porcentaje_ocio_empleado_2']}%)"
        )

        self.lbl_resultados.config(text=texto)

    def exportar_excel(self):
        if self.df_vector_mostrado.empty:
            messagebox.showwarning("Sin datos", "Primero ejecutá una simulación.")
            return

        ruta = exportar_a_excel(
            df_mostrado=self.df_vector_mostrado.fillna("-"),
            df_completo=self.df_vector_completo.fillna("-"),
            resultados=self.ultimo_resultado,
            ruta_salida="output/vector_estado.xlsx"
        )

        messagebox.showinfo("Exportación correcta", f"Archivo generado:\n{ruta}")