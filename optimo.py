import random

def generar_demanda(num_procesos, tiempo):
    return [
        random.randint(1, num_procesos)
        for _ in range(tiempo)
    ]

def leer_desde_archivo(nombre):
    try:
        with open(nombre, "r") as f:
            datos = f.read().split()
        return [int(x) for x in datos]
    except:
        print("❌ Error al leer archivo.")
        return None

def imprimir_tabla(
    frames_historial,
    historial_pro,
    demanda,
    fallos
):
    print("\n*** TABLA FINAL ***\n")
    
    ancho = 5
    
    print("Demanda: ", end="")
    
    for d in demanda:
        print(f"{d:<{ancho}}", end="")
    print()

    print("Fallo:   ", end="")
    
    for f in fallos:
        print(f"{f:<{ancho}}", end="")
    print("\n")

    num_frames = len(frames_historial[0])

    for i in range(num_frames):
        print(f"F{i+1}: ", end="")
        for t in range(len(frames_historial)):
            valor_frame = frames_historial[t][i]
            if valor_frame == -1:
                texto = "-"
            else:
                texto = str(valor_frame)
            print(f"{texto:<{ancho}}", end="")

        print()

def reemplazo_optimo(
    demanda,
    num_frames
):

    frames = [-1] * num_frames
    historial = []
    historial_pro = []
    fallos = []
    total_fallos = 0

    for i in range(len(demanda)):
        pagina = demanda[i]
        if pagina in frames:
            fallos.append("")
        else:
            total_fallos += 1
            fallos.append("X")
            if -1 in frames:
                indice = frames.index(-1)
                frames[indice] = pagina
            else:
                futuras = []
                for f in frames:
                    if f in demanda[i+1:]:
                        distancia = (
                            demanda[i+1:].index(f) + 1
                        )
                        futuras.append(distancia)
                    else:
                        futuras.append(float('inf'))
                reemplazar = futuras.index(
                    max(futuras)
                )

                frames[reemplazar] = pagina
        proximos = []
        
        for f in frames:
            if f == -1:
                proximos.append("-")
            elif f in demanda[i+1:]:
                distancia = (
                    demanda[i+1:].index(f) + 1
                )
                proximos.append(distancia)
            else:
                proximos.append("-")
        historial.append(frames.copy())
        historial_pro.append(proximos.copy())
    return (
        historial,
        historial_pro,
        fallos,
        total_fallos
    )

def mostrar_tabla_inicial(
    num_frames,
    num_procesos,
    tiempo,
    demanda
):

    print("\n*** CONFIGURACION ***")
    print(f"Frames disponibles: {num_frames}")
    print(f"Procesos posibles: 1 - {num_procesos}")
    print(f"Tiempo de simulacion: {tiempo}")
    print("\nDemanda generada:")
    print(demanda)

while True:
    print("\n*** MENU ***")
    print("1. Ingresar demanda manualmente")
    print("2. Leer demanda desde archivo TXT")
    print("3. Generar demanda aleatoria")
    print("4. Salir")

    opcion = input(
        "Seleccione una opcion: "
    )

    if opcion == "4":
        print("Fin del programa.")
        break

    print("\nCONFIGURACION")
    print("1. 4 Frames con 8 procesos")
    print("2. 8 Frames con 16 procesos")

    config = input(
        "Seleccione configuracion: "
    )

    if config == "1":
        num_frames = 4
        num_procesos = 8
    elif config == "2":
        num_frames = 8
        num_procesos = 16
    else:
        print("❌ Configuracion invalida")
        continue

    tiempo = int(
        input(
            "Tiempo de simulacion (10-70): "
        )
    )

    if tiempo < 10 or tiempo > 70:
        print("❌ Tiempo fuera de rango")
        continue

    demanda = []

    if opcion == "1":
        print(
            "\nIngrese la demanda separada por espacios:"
        )
        entrada = input(">> ")
        demanda = [
            int(x)
            for x in entrada.split()
        ]
        if len(demanda) != tiempo:
            print(
                "❌ La cantidad de procesos no coincide con el tiempo."
            )
            continue
    elif opcion == "2":
        nombre = input(
            "Nombre del archivo TXT: "
        )
        demanda = leer_desde_archivo(nombre)
        if demanda is None:
            continue
        if len(demanda) != tiempo:
            print(
                "❌ El archivo no coincide con el tiempo."
            )
            continue
    elif opcion == "3":
        demanda = generar_demanda(
            num_procesos,
            tiempo
        )
    else:
        print("❌ Opcion invalida")
        continue

    mostrar_tabla_inicial(
        num_frames,
        num_procesos,
        tiempo,
        demanda
    )

    (
        historial,
        historial_pro,
        fallos,
        total_fallos
    ) = reemplazo_optimo(
        demanda,
        num_frames
    )

    imprimir_tabla(
        historial,
        historial_pro,
        demanda,
        fallos
    )

    print(
        f"\n *** TOTAL DE FALLOS DE PAGINA: {total_fallos} ***"
    )