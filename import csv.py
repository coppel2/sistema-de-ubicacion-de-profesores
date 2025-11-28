import csv
from datetime import datetime, time

RUTA_ARCHIVO_HORARIO = "horarios.csv"

# --------------------------
# Carga y modelo de datos
# --------------------------

def cargar_horario(ruta_archivo):
    """
    Carga el archivo CSV de horarios y devuelve una lista de diccionarios.
    Cada registro tiene las claves:
    profesor, dia_semana, hora_inicio, hora_fin, aula, edificio, grupo
    """
    horario = []
    with open(ruta_archivo, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            # Normalizamos espacios y dejamos todo como string
            fila_normalizada = {
                "profesor": fila["profesor"].strip(),
                "dia_semana": fila["dia_semana"].strip(),
                "hora_inicio": fila["hora_inicio"].strip(),
                "hora_fin": fila["hora_fin"].strip(),
                "aula": fila["aula"].strip(),
                "edificio": fila["edificio"].strip(),
                "grupo": fila["grupo"].strip(),
            }
            horario.append(fila_normalizada)
    return horario


# --------------------------
# Funciones auxiliares
# --------------------------

def obtener_nombre_dia_espanol(fecha):
    """
    Convierte un objeto datetime a nombre de día en español.
    0 = lunes, 6 = domingo
    """
    dias = [
        "Lunes", "Martes", "Miércoles",
        "Jueves", "Viernes", "Sábado", "Domingo"
    ]
    return dias[fecha.weekday()]


def parsear_hora(hora_str):
    """
    Convierte un string HH:MM a un objeto time.
    """
    return datetime.strptime(hora_str, "%H:%M").time()


def esta_dentro_del_intervalo(hora_actual, hora_inicio, hora_fin):
    """
    Verifica si hora_inicio <= hora_actual < hora_fin
    """
    return hora_inicio <= hora_actual < hora_fin


# --------------------------
# Lógica principal
# --------------------------

def encontrar_ubicacion_actual(horario, nombre_profesor, fecha_hora=None):
    """
    Devuelve la fila del horario que indica dónde debería estar
    el profesor en la fecha/hora indicada.

    Si fecha_hora es None, se usa la fecha/hora actual.
    """
    if fecha_hora is None:
        fecha_hora = datetime.now()

    dia_hoy = obtener_nombre_dia_espanol(fecha_hora)
    hora_actual = fecha_hora.time()
    nombre_profesor = nombre_profesor.strip().lower()

    posibles_clases = []

    for fila in horario:
        if fila["profesor"].strip().lower() != nombre_profesor:
            continue

        if fila["dia_semana"] != dia_hoy:
            continue

        hora_inicio = parsear_hora(fila["hora_inicio"])
        hora_fin = parsear_hora(fila["hora_fin"])

        if esta_dentro_del_intervalo(hora_actual, hora_inicio, hora_fin):
            posibles_clases.append(fila)

    # En la mayoría de los casos habrá 0 o 1 coincidencia.
    if not posibles_clases:
        return None

    # Si hubiese más de una, devolvemos la primera (o podrías manejar conflictos aquí)
    return posibles_clases[0]


def mostrar_horario_profesor(horario, nombre_profesor):
    """
    Imprime en pantalla todo el horario de un profesor.
    """
    nombre_profesor = nombre_profesor.strip().lower()
    registros = [fila for fila in horario
                 if fila["profesor"].strip().lower() == nombre_profesor]

    if not registros:
        print(f"No se encontraron registros para el profesor: {nombre_profesor}")
        return

    # Ordenamos por día y hora
    orden_dias = {
        "Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4,
        "Viernes": 5, "Sábado": 6, "Domingo": 7
    }

    registros.sort(
        key=lambda x: (
            orden_dias.get(x["dia_semana"], 99),
            parsear_hora(x["hora_inicio"])
        )
    )

    print(f"\nHorario del profesor: {registros[0]['profesor']}")
    print("-" * 60)
    for fila in registros:
        print(
            f"{fila['dia_semana']:10} "
            f"{fila['hora_inicio']}-{fila['hora_fin']:5}  "
            f"Aula: {fila['aula']:<15} Edificio: {fila['edificio']:<10} "
            f"Grupo: {fila['grupo']}"
        )
    print("-" * 60)


# --------------------------
# Interfaz de línea de comandos
# --------------------------

def menu_principal():
    horario = cargar_horario(RUTA_ARCHIVO_HORARIO)

    while True:
        print("\n=== Sistema de Ubicación de Profesores ===")
        print("1) Ver horario completo de un profesor")
        print("2) Ver ubicación actual de un profesor")
        print("3) Ver ubicación de un profesor en una fecha/hora específica")
        print("0) Salir")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            nombre = input("Nombre del profesor: ")
            mostrar_horario_profesor(horario, nombre)

        elif opcion == "2":
            nombre = input("Nombre del profesor: ")
            registro = encontrar_ubicacion_actual(horario, nombre)

            if registro is None:
                print("El profesor no tiene clase asignada en este momento "
                      "según el horario.")
            else:
                print(f"\nSegún el horario, en este momento el profesor "
                      f"{registro['profesor']} debería estar en:")
                print(f"  Aula: {registro['aula']}")
                print(f"  Edificio: {registro['edificio']}")
                print(f"  Grupo: {registro['grupo']}")
                print(f"  Horario: {registro['dia_semana']} "
                      f"{registro['hora_inicio']} - {registro['hora_fin']}")

        elif opcion == "3":
            nombre = input("Nombre del profesor: ")
            fecha_str = input(
                "Fecha (formato YYYY-MM-DD), por ejemplo 2025-03-18: "
            ).strip()
            hora_str = input(
                "Hora (formato HH:MM en 24 horas), por ejemplo 09:30: "
            ).strip()

            try:
                fecha_hora = datetime.strptime(
                    f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M"
                )
            except ValueError:
                print("⚠️ Formato de fecha u hora inválido.")
                continue

            registro = encontrar_ubicacion_actual(horario, nombre, fecha_hora)

            if registro is None:
                print("El profesor no tiene clase asignada en ese momento.")
            else:
                print(f"\nSegún el horario, el {fecha_str} a las {hora_str} "
                      f"el profesor {registro['profesor']} debería estar en:")
                print(f"  Aula: {registro['aula']}")
                print(f"  Edificio: {registro['edificio']}")
                print(f"  Grupo: {registro['grupo']}")
                print(f"  Horario oficial: {registro['dia_semana']} "
                      f"{registro['hora_inicio']} - {registro['hora_fin']}")

        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu_principal()
