import math


# ==========================
# Configuración editable
# ==========================

MAX_ITERACIONES_PERMITIDAS = 100000
MAX_FILAS_MOSTRAR = 500
MAX_CAPACIDAD_PERMITIDA = 500
#facu
MAX_MEDIA_PRESTAMO = 1000
MAX_MEDIA_LECTURA = 1000
MAX_TIEMPO_UNIFORME = 1000

TOLERANCIA_PROBABILIDADES = 0.0001

CAMPOS_ENTEROS = [
    "cantidad_iteraciones_mostrar",
    "max_iteraciones",
    "capacidad_maxima",
]

CAMPOS_DECIMALES = [
    "tiempo_maximo",
    "hora_desde",
    "tiempo_entre_llegadas",
    "prob_prestamo",
    "prob_devolucion",
    "prob_consulta",
    "consulta_min",
    "consulta_max",
    "media_prestamo",
    "devolucion_min",
    "devolucion_max",
    "prob_se_retira",
    "prob_lee_en_sala",
    "media_lectura",
]


# ==========================
# Validaciones mientras escribe
# ==========================

def es_texto_entero_valido(valor):
    """
    Permite que el campo quede vacío mientras el usuario borra.
    Si no está vacío, solo acepta dígitos.
    """
    if valor == "":
        return True

    return valor.isdigit()


def es_texto_decimal_valido(valor):
    """
    Permite números decimales con punto o coma.
    No permite letras.
    """
    if valor == "":
        return True

    valor = valor.replace(",", ".")

    if valor.count(".") > 1:
        return False

    if valor == ".":
        return False

    try:
        float(valor)
        return True
    except ValueError:
        return False


# ==========================
# Parseo seguro
# ==========================

def convertir_valor(clave, valor):
    valor = valor.strip().replace(",", ".")

    if valor == "":
        raise ValueError(f"El parámetro '{clave}' no puede estar vacío.")

    if clave in CAMPOS_ENTEROS:
        if not valor.isdigit():
            raise ValueError(f"El parámetro '{clave}' debe ser un número entero positivo.")

        return int(valor)

    try:
        numero = float(valor)
    except ValueError:
        raise ValueError(f"El parámetro '{clave}' debe ser numérico válido.")

    if math.isnan(numero) or math.isinf(numero):
        raise ValueError(f"El parámetro '{clave}' no puede ser infinito ni NaN.")

    return numero


# ==========================
# Validador principal
# ==========================

def validar_parametros(parametros):
    validar_existencia_campos(parametros)
    validar_tipos_generales(parametros)

    validar_simulacion(parametros)
    validar_llegadas(parametros)

    validar_probabilidades_tramite(parametros)
    validar_consulta(parametros)
    validar_prestamo(parametros)
    validar_devolucion(parametros)
    validar_post_prestamo(parametros)
    validar_lectura(parametros)

    validar_capacidad(parametros)
    validar_consistencia_general(parametros)


# ==========================
# Validaciones base
# ==========================

def validar_existencia_campos(parametros):
    campos_requeridos = CAMPOS_ENTEROS + CAMPOS_DECIMALES

    for campo in campos_requeridos:
        if campo not in parametros:
            raise ValueError(f"Falta el parámetro requerido: {campo}")


def validar_tipos_generales(parametros):
    for campo in CAMPOS_ENTEROS:
        if not isinstance(parametros[campo], int):
            raise ValueError(f"El parámetro '{campo}' debe ser entero.")

    for campo in CAMPOS_DECIMALES:
        if not isinstance(parametros[campo], (int, float)):
            raise ValueError(f"El parámetro '{campo}' debe ser numérico.")

        if math.isnan(parametros[campo]) or math.isinf(parametros[campo]):
            raise ValueError(f"El parámetro '{campo}' no puede ser infinito ni NaN.")


# ==========================
# Validaciones de simulación
# ==========================

def validar_simulacion(parametros):
    tiempo_maximo = parametros["tiempo_maximo"]
    hora_desde = parametros["hora_desde"]
    cantidad_iteraciones_mostrar = parametros["cantidad_iteraciones_mostrar"]
    max_iteraciones = parametros["max_iteraciones"]

    if tiempo_maximo <= 0:
        raise ValueError("El tiempo máximo X debe ser mayor a 0.")

    if hora_desde < 0:
        raise ValueError("La hora desde j no puede ser negativa.")

    if hora_desde > tiempo_maximo:
        raise ValueError("La hora desde j no puede ser mayor al tiempo máximo X.")

    if cantidad_iteraciones_mostrar <= 0:
        raise ValueError("La cantidad de iteraciones i debe ser mayor a 0.")

    if cantidad_iteraciones_mostrar > MAX_FILAS_MOSTRAR:
        raise ValueError(
            f"La cantidad de iteraciones i no puede superar {MAX_FILAS_MOSTRAR}. "
            "Esto evita problemas de memoria al dibujar el vector en pantalla."
        )

    if max_iteraciones <= 0:
        raise ValueError("El máximo de iteraciones N debe ser mayor a 0.")

    if max_iteraciones > MAX_ITERACIONES_PERMITIDAS:
        raise ValueError(
            f"El máximo de iteraciones N no puede superar {MAX_ITERACIONES_PERMITIDAS}, "
            "según la consigna del TP."
        )

    if max_iteraciones < cantidad_iteraciones_mostrar:
        raise ValueError(
            "El máximo de iteraciones N debe ser mayor o igual a la cantidad de iteraciones i."
        )


def validar_llegadas(parametros):
    tiempo_entre_llegadas = parametros["tiempo_entre_llegadas"]

    if tiempo_entre_llegadas <= 0:
        raise ValueError("El tiempo entre llegadas debe ser mayor a 0.")

    if tiempo_entre_llegadas < 0.0001:
        raise ValueError("El tiempo entre llegadas es demasiado pequeño y puede generar demasiados eventos.")


# ==========================
# Probabilidades
# ==========================

def validar_probabilidad(nombre, valor):
    if valor < 0 or valor > 1:
        raise ValueError(f"La probabilidad '{nombre}' debe estar entre 0 y 1.")


def validar_suma_probabilidades(nombre_grupo, probabilidades):
    suma = sum(probabilidades)

    if abs(suma - 1) > TOLERANCIA_PROBABILIDADES:
        raise ValueError(f"Las probabilidades de {nombre_grupo} deben sumar 1. Actualmente suman {round(suma, 6)}.")


def validar_probabilidades_tramite(parametros):
    prob_prestamo = parametros["prob_prestamo"]
    prob_devolucion = parametros["prob_devolucion"]
    prob_consulta = parametros["prob_consulta"]

    validar_probabilidad("Prob. préstamo", prob_prestamo)
    validar_probabilidad("Prob. devolución", prob_devolucion)
    validar_probabilidad("Prob. consulta", prob_consulta)

    validar_suma_probabilidades(
        "préstamo, devolución y consulta",
        [prob_prestamo, prob_devolucion, prob_consulta]
    )


def validar_post_prestamo(parametros):
    prob_se_retira = parametros["prob_se_retira"]
    prob_lee_en_sala = parametros["prob_lee_en_sala"]

    validar_probabilidad("Prob. se retira", prob_se_retira)
    validar_probabilidad("Prob. lee en sala", prob_lee_en_sala)

    validar_suma_probabilidades(
        "decisión posterior al préstamo",
        [prob_se_retira, prob_lee_en_sala]
    )


# ==========================
# Distribuciones
# ==========================

def validar_consulta(parametros):
    consulta_min = parametros["consulta_min"]
    consulta_max = parametros["consulta_max"]

    if consulta_min < 0:
        raise ValueError("Consulta mín. no puede ser negativa.")

    if consulta_max <= 0:
        raise ValueError("Consulta máx. debe ser mayor a 0.")

    if consulta_max <= consulta_min:
        raise ValueError("Consulta máx. debe ser mayor que Consulta mín.")

    if consulta_max > MAX_TIEMPO_UNIFORME:
        raise ValueError(f"Consulta máx. no puede superar {MAX_TIEMPO_UNIFORME} minutos.")
    


def validar_prestamo(parametros):
    media_prestamo = parametros["media_prestamo"]

    if media_prestamo <= 0:
        raise ValueError("La media de préstamo debe ser mayor a 0.")

    if media_prestamo > MAX_MEDIA_PRESTAMO:
        raise ValueError(f"La media de préstamo no puede superar {MAX_MEDIA_PRESTAMO} minutos.")


def validar_devolucion(parametros):
    devolucion_min = parametros["devolucion_min"]
    devolucion_max = parametros["devolucion_max"]

    if devolucion_min < 0:
        raise ValueError("Devolución mín. no puede ser negativa.")

    if devolucion_max <= 0:
        raise ValueError("Devolución máx. debe ser mayor a 0.")

    if devolucion_max <= devolucion_min:
        raise ValueError("Devolución máx. debe ser mayor que Devolución mín.")

    if devolucion_max > MAX_TIEMPO_UNIFORME:
        raise ValueError(f"Devolución máx. no puede superar {MAX_TIEMPO_UNIFORME} minutos.")


def validar_lectura(parametros):
    media_lectura = parametros["media_lectura"]

    if media_lectura <= 0:
        raise ValueError("La media de lectura debe ser mayor a 0.")

    if media_lectura > MAX_MEDIA_LECTURA:
        raise ValueError(f"La media de lectura no puede superar {MAX_MEDIA_LECTURA} minutos.")


# ==========================
# Capacidad
# ==========================

def validar_capacidad(parametros):
    capacidad_maxima = parametros["capacidad_maxima"]

    if capacidad_maxima <= 0:
        raise ValueError("La capacidad máxima debe ser mayor a 0.")

    if capacidad_maxima > MAX_CAPACIDAD_PERMITIDA:
        raise ValueError(
            f"La capacidad máxima no puede superar {MAX_CAPACIDAD_PERMITIDA}. "
            "Una capacidad demasiado grande genera demasiadas columnas de objetos temporales."
        )


# ==========================
# Validaciones cruzadas
# ==========================

def validar_consistencia_general(parametros):
    prob_prestamo = parametros["prob_prestamo"]
    prob_lee_en_sala = parametros["prob_lee_en_sala"]

    if prob_prestamo == 0 and prob_lee_en_sala > 0:
        raise ValueError(
            "Prob. lee en sala no debería ser mayor a 0 si Prob. préstamo es 0, "
            "porque solo leen quienes pidieron préstamo."
        )

    if parametros["tiempo_maximo"] < parametros["tiempo_entre_llegadas"]:
        raise ValueError(
            "El tiempo máximo X es menor que el tiempo entre llegadas. "
            "La simulación podría terminar sin procesar ninguna llegada."
        )