import json
import os


# ============================================================
# ARCHIVOS JSON
# ============================================================

ARCHIVO_EVENTOS = "eventos.json"
ARCHIVO_ARTISTAS = "artistas.json"
ARCHIVO_ASISTENTES = "asistentes.json"


# ============================================================
# FUNCIONES PARA GUARDAR Y CARGAR JSON
# ============================================================

def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def cargar_json(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return {}

    try:
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except json.JSONDecodeError:
        return {}


# ============================================================
# CLASE ASISTENTE
# ============================================================

class Asistente:

    def __init__(
        self,
        identificacion,
        nombre,
        correo,
        tipo_boleto,
        inscripciones=None
    ):
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo
        self.tipo_boleto = tipo_boleto
        self.inscripciones = inscripciones or {}

    def convertir_a_diccionario(self):
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "correo": self.correo,
            "tipo_boleto": self.tipo_boleto,
            "inscripciones": self.inscripciones
        }

    def __str__(self):
        return (
            f"ID: {self.identificacion} | "
            f"Nombre: {self.nombre} | "
            f"Correo: {self.correo} | "
            f"Boleto: {self.tipo_boleto}"
        )


# ============================================================
# CLASE ARTISTA
# ============================================================

class Artista:

    def __init__(
        self,
        identificacion,
        nombre,
        tipo_presentacion,
        duracion,
        eventos=None
    ):
        self.identificacion = identificacion
        self.nombre = nombre
        self.tipo_presentacion = tipo_presentacion
        self.duracion = duracion
        self.eventos = eventos or []

    def convertir_a_diccionario(self):
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "tipo_presentacion": self.tipo_presentacion,
            "duracion": self.duracion,
            "eventos": self.eventos
        }

    def __str__(self):
        return (
            f"ID: {self.identificacion} | "
            f"Nombre: {self.nombre} | "
            f"Presentación: {self.tipo_presentacion} | "
            f"Duración: {self.duracion} minutos"
        )


# ============================================================
# CLASE EVENTO
# ============================================================

class Evento:

    def __init__(
        self,
        codigo,
        nombre,
        fecha,
        hora,
        lugar,
        capacidad,
        artistas=None,
        asistentes=None
    ):
        self.codigo = codigo
        self.nombre = nombre
        self.fecha = fecha
        self.hora = hora
        self.lugar = lugar
        self.capacidad = capacidad
        self.artistas = artistas or []
        self.asistentes = asistentes or {}

    def convertir_a_diccionario(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "fecha": self.fecha,
            "hora": self.hora,
            "lugar": self.lugar,
            "capacidad": self.capacidad,
            "artistas": self.artistas,
            "asistentes": self.asistentes
        }

    def cupos_disponibles(self):

        confirmados = sum(
            1
            for estado in self.asistentes.values()
            if estado == "CONFIRMADO"
        )

        return self.capacidad - confirmados

    def esta_lleno(self):
        return self.cupos_disponibles() <= 0

    def porcentaje_asistencia(self):

        if self.capacidad == 0:
            return 0

        confirmados = sum(
            1
            for estado in self.asistentes.values()
            if estado == "CONFIRMADO"
        )

        return (confirmados / self.capacidad) * 100

    def agregar_artista(self, identificacion):

        if identificacion in self.artistas:
            return False

        self.artistas.append(identificacion)

        return True

    def registrar_asistente(self, identificacion):

        if identificacion in self.asistentes:

            if self.asistentes[identificacion] == "CONFIRMADO":
                return False, "El asistente ya está registrado."

            if self.asistentes[identificacion] == "CANCELADO":

                if self.esta_lleno():
                    return False, "El evento está lleno."

                self.asistentes[identificacion] = "CONFIRMADO"

                return True, "Inscripción reactivada."

        if self.esta_lleno():
            return False, "El evento ha alcanzado su capacidad máxima."

        self.asistentes[identificacion] = "CONFIRMADO"

        return True, "Asistente registrado correctamente."

    def cancelar_asistente(self, identificacion):

        if identificacion not in self.asistentes:
            return False

        if self.asistentes[identificacion] != "CONFIRMADO":
            return False

        self.asistentes[identificacion] = "CANCELADO"

        return True

    def mostrar(self):

        print("\n--------------------------------------------")
        print(f"Código: {self.codigo}")
        print(f"Evento: {self.nombre}")
        print(f"Fecha: {self.fecha}")
        print(f"Hora: {self.hora}")
        print(f"Lugar: {self.lugar}")
        print(f"Capacidad: {self.capacidad}")
        print(f"Cupos disponibles: {self.cupos_disponibles()}")
        print(f"Asistencia: {self.porcentaje_asistencia():.1f}%")
        print("--------------------------------------------")


# ============================================================
# SISTEMA CULTUVIVO
# ============================================================

class SistemaCultuVivo:

    def __init__(self):

        self.eventos = {}
        self.artistas = {}
        self.asistentes = {}

        self.cargar_datos()

    # ========================================================
    # CARGAR DATOS
    # ========================================================

    def cargar_datos(self):

        datos_eventos = cargar_json(ARCHIVO_EVENTOS)
        datos_artistas = cargar_json(ARCHIVO_ARTISTAS)
        datos_asistentes = cargar_json(ARCHIVO_ASISTENTES)

        # Eventos
        for codigo, datos in datos_eventos.items():

            self.eventos[codigo] = Evento(
                datos["codigo"],
                datos["nombre"],
                datos["fecha"],
                datos["hora"],
                datos["lugar"],
                datos["capacidad"],
                datos.get("artistas", []),
                datos.get("asistentes", {})
            )

        # Artistas
        for identificacion, datos in datos_artistas.items():

            self.artistas[identificacion] = Artista(
                datos["identificacion"],
                datos["nombre"],
                datos["tipo_presentacion"],
                datos["duracion"],
                datos.get("eventos", [])
            )

        # Asistentes
        for identificacion, datos in datos_asistentes.items():

            self.asistentes[identificacion] = Asistente(
                datos["identificacion"],
                datos["nombre"],
                datos["correo"],
                datos["tipo_boleto"],
                datos.get("inscripciones", {})
            )

    # ========================================================
    # GUARDAR TODOS LOS DATOS
    # ========================================================

    def guardar_todo(self):

        eventos = {}

        for codigo, evento in self.eventos.items():
            eventos[codigo] = evento.convertir_a_diccionario()

        artistas = {}

        for identificacion, artista in self.artistas.items():
            artistas[identificacion] = artista.convertir_a_diccionario()

        asistentes = {}

        for identificacion, asistente in self.asistentes.items():
            asistentes[identificacion] = asistente.convertir_a_diccionario()

        guardar_json(
            ARCHIVO_EVENTOS,
            eventos
        )

        guardar_json(
            ARCHIVO_ARTISTAS,
            artistas
        )

        guardar_json(
            ARCHIVO_ASISTENTES,
            asistentes
        )

    # ========================================================
    # FUNCIONES GENERALES
    # ========================================================

    def pausa(self):
        input("\nPresiona ENTER para continuar...")

    def leer_entero(self, mensaje):

        while True:

            try:

                numero = int(input(mensaje))

                if numero < 0:
                    print("Ingresa un número positivo.")
                    continue

                return numero

            except ValueError:
                print("Ingresa un número válido.")

    # ========================================================
    # EVENTOS
    # ========================================================

    def crear_evento(self):

        print("\n========== CREAR EVENTO ==========")

        codigo = input("Código del evento: ").strip()

        if codigo in self.eventos:
            print("Ya existe un evento con ese código.")
            return

        nombre = input("Nombre del evento: ").strip()
        fecha = input("Fecha (DD/MM/AAAA): ").strip()
        hora = input("Hora (HH:MM): ").strip()
        lugar = input("Lugar: ").strip()

        capacidad = self.leer_entero(
            "Capacidad máxima: "
        )

        if capacidad <= 0:
            print("La capacidad debe ser mayor que cero.")
            return

        evento = Evento(
            codigo,
            nombre,
            fecha,
            hora,
            lugar,
            capacidad
        )

        self.eventos[codigo] = evento

        self.guardar_todo()

        print("Evento creado y guardado correctamente.")

    def listar_eventos(self):

        print("\n========== EVENTOS ==========")

        if not self.eventos:
            print("No existen eventos registrados.")
            return

        for evento in self.eventos.values():
            evento.mostrar()

    def modificar_evento(self):

        print("\n========== MODIFICAR EVENTO ==========")

        codigo = input("Código del evento: ").strip()

        evento = self.eventos.get(codigo)

        if evento is None:
            print("Evento no encontrado.")
            return

        print("Deja vacío un campo para mantener el valor actual.")

        nombre = input(
            f"Nombre [{evento.nombre}]: "
        ).strip()

        fecha = input(
            f"Fecha [{evento.fecha}]: "
        ).strip()

        hora = input(
            f"Hora [{evento.hora}]: "
        ).strip()

        lugar = input(
            f"Lugar [{evento.lugar}]: "
        ).strip()

        if nombre:
            evento.nombre = nombre

        if fecha:
            evento.fecha = fecha

        if hora:
            evento.hora = hora

        if lugar:
            evento.lugar = lugar

        capacidad = input(
            f"Capacidad [{evento.capacidad}]: "
        ).strip()

        if capacidad:

            try:

                nueva_capacidad = int(capacidad)

                confirmados = sum(
                    1
                    for estado in evento.asistentes.values()
                    if estado == "CONFIRMADO"
                )

                if nueva_capacidad < confirmados:
                    print(
                        "La capacidad no puede ser menor "
                        "que los asistentes confirmados."
                    )
                    return

                evento.capacidad = nueva_capacidad

            except ValueError:
                print("Capacidad inválida.")
                return

        self.guardar_todo()

        print("Evento modificado y guardado correctamente.")

    # ========================================================
    # ARTISTAS
    # ========================================================

    def registrar_artista(self):

        print("\n========== REGISTRAR ARTISTA ==========")

        identificacion = input(
            "Identificación: "
        ).strip()

        if identificacion in self.artistas:
            print("El artista ya existe.")
            return

        nombre = input("Nombre: ").strip()

        tipo = input(
            "Tipo de presentación: "
        ).strip()

        duracion = self.leer_entero(
            "Duración en minutos: "
        )

        artista = Artista(
            identificacion,
            nombre,
            tipo,
            duracion
        )

        self.artistas[identificacion] = artista

        self.guardar_todo()

        print("Artista registrado y guardado correctamente.")

    def listar_artistas(self):

        print("\n========== ARTISTAS ==========")

        if not self.artistas:
            print("No existen artistas.")
            return

        for artista in self.artistas.values():
            print(artista)

    def asignar_artista(self):

        print("\n========== ASIGNAR ARTISTA ==========")

        codigo = input(
            "Código del evento: "
        ).strip()

        evento = self.eventos.get(codigo)

        if evento is None:
            print("Evento no encontrado.")
            return

        identificacion = input(
            "Identificación del artista: "
        ).strip()

        artista = self.artistas.get(identificacion)

        if artista is None:
            print("Artista no encontrado.")
            return

        if not evento.agregar_artista(identificacion):
            print("El artista ya está asignado.")
            return

        if codigo not in artista.eventos:
            artista.eventos.append(codigo)

        self.guardar_todo()

        print("Artista asignado correctamente.")

    def agenda_artista(self):

        print("\n========== AGENDA DEL ARTISTA ==========")

        identificacion = input(
            "Identificación del artista: "
        ).strip()

        artista = self.artistas.get(identificacion)

        if artista is None:
            print("Artista no encontrado.")
            return

        print(f"\nAgenda de {artista.nombre}")

        if not artista.eventos:
            print("No tiene eventos asignados.")
            return

        for codigo in artista.eventos:

            evento = self.eventos.get(codigo)

            if evento:

                print(
                    f"- {evento.nombre} | "
                    f"{evento.fecha} | "
                    f"{evento.hora} | "
                    f"{evento.lugar}"
                )

    # ========================================================
    # ASISTENTES
    # ========================================================

    def registrar_asistente(self):

        print("\n========== REGISTRAR ASISTENTE ==========")

        identificacion = input(
            "Identificación: "
        ).strip()

        if identificacion in self.asistentes:
            print("El asistente ya existe.")
            return

        nombre = input("Nombre completo: ").strip()

        correo = input(
            "Correo electrónico: "
        ).strip()

        tipo_boleto = input(
            "Tipo de boleto: "
        ).strip()

        asistente = Asistente(
            identificacion,
            nombre,
            correo,
            tipo_boleto
        )

        self.asistentes[identificacion] = asistente

        self.guardar_todo()

        print("Asistente registrado correctamente.")

    def registrar_asistente_evento(self):

        print("\n========== INSCRIBIR ASISTENTE ==========")

        identificacion = input(
            "Identificación del asistente: "
        ).strip()

        asistente = self.asistentes.get(identificacion)

        if asistente is None:
            print("El asistente no existe.")
            return

        codigo = input(
            "Código del evento: "
        ).strip()

        evento = self.eventos.get(codigo)

        if evento is None:
            print("El evento no existe.")
            return

        correcto, mensaje = evento.registrar_asistente(
            identificacion
        )

        print(mensaje)

        if correcto:

            asistente.inscripciones[codigo] = "CONFIRMADO"

            self.guardar_todo()

    def cancelar_inscripcion(self):

        print("\n========== CANCELAR INSCRIPCIÓN ==========")

        identificacion = input(
            "Identificación del asistente: "
        ).strip()

        asistente = self.asistentes.get(identificacion)

        if asistente is None:
            print("Asistente no encontrado.")
            return

        codigo = input(
            "Código del evento: "
        ).strip()

        evento = self.eventos.get(codigo)

        if evento is None:
            print("Evento no encontrado.")
            return

        if evento.cancelar_asistente(identificacion):

            asistente.inscripciones[codigo] = "CANCELADO"

            self.guardar_todo()

            print("Inscripción cancelada correctamente.")

        else:
            print("No se pudo cancelar la inscripción.")

    def consultar_inscripciones(self):

        print("\n========== INSCRIPCIONES ==========")

        identificacion = input(
            "Identificación del asistente: "
        ).strip()

        asistente = self.asistentes.get(identificacion)

        if asistente is None:
            print("Asistente no encontrado.")
            return

        print(f"\nAsistente: {asistente.nombre}")

        if not asistente.inscripciones:
            print("No tiene inscripciones.")
            return

        for codigo, estado in asistente.inscripciones.items():

            evento = self.eventos.get(codigo)

            if evento:

                print(
                    f"- {evento.nombre} | "
                    f"{evento.fecha} | "
                    f"{evento.hora} | "
                    f"Estado: {estado}"
                )

    # ========================================================
    # REPORTES
    # ========================================================

    def reporte_eventos(self):

        print("\n========== REPORTE DE EVENTOS ==========")

        for evento in self.eventos.values():

            confirmados = sum(
                1
                for estado in evento.asistentes.values()
                if estado == "CONFIRMADO"
            )

            print(
                f"\nEvento: {evento.nombre}"
            )

            print(
                f"Fecha: {evento.fecha}"
            )

            print(
                f"Lugar: {evento.lugar}"
            )

            print(
                f"Asistentes: "
                f"{confirmados}/{evento.capacidad}"
            )

            print(
                f"Asistencia: "
                f"{evento.porcentaje_asistencia():.1f}%"
            )

    def reporte_artistas_por_evento(self):

        print("\n========== ARTISTAS POR EVENTO ==========")

        for evento in self.eventos.values():

            print(f"\n{evento.nombre}:")

            if not evento.artistas:
                print("  No hay artistas.")

            for identificacion in evento.artistas:

                artista = self.artistas.get(
                    identificacion
                )

                if artista:
                    print(
                        f"  - {artista.nombre} "
                        f"({artista.tipo_presentacion})"
                    )

    def reporte_asistentes(self):

        print("\n========== ASISTENTES ==========")

        for asistente in self.asistentes.values():

            print(f"\n{asistente}")

            for codigo, estado in asistente.inscripciones.items():

                evento = self.eventos.get(codigo)

                if evento:

                    print(
                        f"  - {evento.nombre}: "
                        f"{estado}"
                    )

    def reporte_baja_asistencia(self):

        print(
            "\n========== BAJA ASISTENCIA =========="
        )

        encontrados = False

        for evento in self.eventos.values():

            if evento.porcentaje_asistencia() < 50:

                encontrados = True

                print(
                    f"- {evento.nombre}: "
                    f"{evento.porcentaje_asistencia():.1f}%"
                )

        if not encontrados:
            print(
                "No hay eventos con asistencia inferior al 50%."
            )

    # ========================================================
    # MENÚ REPORTES
    # ========================================================

    def menu_reportes(self):

        while True:

            print("\n========== REPORTES ==========")
            print("1. Eventos")
            print("2. Artistas por evento")
            print("3. Asistentes")
            print("4. Baja asistencia")
            print("5. Volver")

            opcion = input(
                "Selecciona una opción: "
            )

            if opcion == "1":
                self.reporte_eventos()
                self.pausa()

            elif opcion == "2":
                self.reporte_artistas_por_evento()
                self.pausa()

            elif opcion == "3":
                self.reporte_asistentes()
                self.pausa()

            elif opcion == "4":
                self.reporte_baja_asistencia()
                self.pausa()

            elif opcion == "5":
                break

            else:
                print("Opción inválida.")

    # ========================================================
    # MENÚ ADMINISTRADOR
    # ========================================================

    def menu_administrador(self):

        while True:

            print("\n===================================")
            print("       MENÚ ADMINISTRADOR")
            print("===================================")
            print("1. Crear evento")
            print("2. Listar eventos")
            print("3. Modificar evento")
            print("4. Registrar artista")
            print("5. Listar artistas")
            print("6. Asignar artista")
            print("7. Reportes")
            print("8. Volver")

            opcion = input(
                "Selecciona una opción: "
            )

            if opcion == "1":
                self.crear_evento()
                self.pausa()

            elif opcion == "2":
                self.listar_eventos()
                self.pausa()

            elif opcion == "3":
                self.modificar_evento()
                self.pausa()

            elif opcion == "4":
                self.registrar_artista()
                self.pausa()

            elif opcion == "5":
                self.listar_artistas()
                self.pausa()

            elif opcion == "6":
                self.asignar_artista()
                self.pausa()

            elif opcion == "7":
                self.menu_reportes()

            elif opcion == "8":
                break

            else:
                print("Opción inválida.")

    # ========================================================
    # MENÚ ASISTENTE
    # ========================================================

    def menu_asistente(self):

        while True:

            print("\n===================================")
            print("          MENÚ ASISTENTE")
            print("===================================")
            print("1. Ver eventos")
            print("2. Registrarme en evento")
            print("3. Consultar inscripciones")
            print("4. Cancelar inscripción")
            print("5. Volver")

            opcion = input(
                "Selecciona una opción: "
            )

            if opcion == "1":
                self.listar_eventos()
                self.pausa()

            elif opcion == "2":
                self.registrar_asistente_evento()
                self.pausa()

            elif opcion == "3":
                self.consultar_inscripciones()
                self.pausa()

            elif opcion == "4":
                self.cancelar_inscripcion()
                self.pausa()

            elif opcion == "5":
                break

            else:
                print("Opción inválida.")

    # ========================================================
    # MENÚ ARTISTA
    # ========================================================

    def menu_artista(self):

        while True:

            print("\n===================================")
            print("           MENÚ ARTISTA")
            print("===================================")
            print("1. Ver mi agenda")
            print("2. Ver eventos")
            print("3. Volver")

            opcion = input(
                "Selecciona una opción: "
            )

            if opcion == "1":
                self.agenda_artista()
                self.pausa()

            elif opcion == "2":
                self.listar_eventos()
                self.pausa()

            elif opcion == "3":
                break

            else:
                print("Opción inválida.")

    # ========================================================
    # MENÚ PRINCIPAL
    # ========================================================

    def iniciar(self):

        while True:

            print("\n")
            print("============================================")
            print("       SISTEMA CULTUVIVO")
            print("  GESTIÓN DE EVENTOS CULTURALES")
            print("============================================")
            print("1. Administrador")
            print("2. Asistente")
            print("3. Artista")
            print("4. Salir")

            opcion = input(
                "Selecciona tu tipo de usuario: "
            )

            if opcion == "1":
                self.menu_administrador()

            elif opcion == "2":
                self.menu_asistente()

            elif opcion == "3":
                self.menu_artista()

            elif opcion == "4":
                self.guardar_todo()

                print("\nDatos guardados correctamente.")
                print("Gracias por utilizar CultuVivo.")
                break

            else:
                print("Opción inválida.")


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    sistema = SistemaCultuVivo()

    sistema.iniciar()