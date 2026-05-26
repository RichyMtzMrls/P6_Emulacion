from collections import deque
import time

ANCHO     = 78
SEP       = "─" * ANCHO
SEP_DOBLE = "═" * ANCHO

PROCESOS_BASE = [
    {"pid": "P0", "llegada": 0, "ejecucion": 5},
    {"pid": "P1", "llegada": 1, "ejecucion": 3},
    {"pid": "P2", "llegada": 2, "ejecucion": 8},
    {"pid": "P3", "llegada": 3, "ejecucion": 2},
    {"pid": "P4", "llegada": 4, "ejecucion": 6},
    {"pid": "P5", "llegada": 5, "ejecucion": 4},
    {"pid": "P6", "llegada": 6, "ejecucion": 7},
    {"pid": "P7", "llegada": 7, "ejecucion": 1},
    {"pid": "P8", "llegada": 8, "ejecucion": 9},
    {"pid": "P9", "llegada": 9, "ejecucion": 3},
]


def imprimir_encabezado():
    print()
    print("╔" + "═" * ANCHO + "╗")
    print("║" + "SIMULACIÓN DE SO  —  ROUND ROBIN".center(ANCHO) + "║")
    print("╚" + "═" * ANCHO + "╝")
    print()


def imprimir_seccion(titulo):
    print()
    print(titulo)
    print(SEP)


def imprimir_tabla_procesos(procesos):
    imprimir_seccion("TABLA DE PROCESOS")
    print("  ┌──────┬────────────┬─────────────┐")
    print("  │  PID │  T.Llegada │  T.Ejecución│")
    print("  ├──────┼────────────┼─────────────┤")
    for p in procesos:
        print(f"  │  {p['pid']:<3} │     {p['llegada']:<5}  │      {p['ejecucion']:<6} │")
    print("  └──────┴────────────┴─────────────┘")


def pedir_quantum():
    print()
    while True:
        try:
            q = int(input("  Ingresa el quantum (unidades de tiempo, ej. 2): "))
            if q >= 1:
                return q
            print("  El quantum debe ser al menos 1.")
        except ValueError:
            print("  Ingresa un número entero válido.")


def imprimir_gantt(gantt, procesos):
    imprimir_seccion("DIAGRAMA DE GANTT — ROUND ROBIN")

    duracion_total = len(gantt)
    pids     = [p["pid"] for p in procesos]
    llegadas = {p["pid"]: p["llegada"] for p in procesos}

    fin_proceso = {}
    for t, pid in enumerate(gantt):
        fin_proceso[pid] = t + 1

    for pid in pids:
        llegada = llegadas[pid]
        fin     = fin_proceso.get(pid, duracion_total)
        fila    = ""
        for t in range(duracion_total):
            if gantt[t] == pid:
                fila += "█"
            elif llegada <= t < fin:
                fila += "░"
            else:
                fila += " "
        print(f"  {pid} │{fila}│")

    print("     └" + "─" * duracion_total + "┘")

    nums = "      "
    for t in range(0, duracion_total + 1, 5):
        nums += str(t).ljust(5)
    print(nums)

    print()
    print("  Leyenda:  █ Ejecutando   ░ En espera   (espacio) No llegó / Ya terminó")


def imprimir_tabla_resultados(resultados):
    imprimir_seccion("RESULTADOS — ROUND ROBIN")
    print("  ┌──────┬─────────┬───────┬───────────┬─────────┐")
    print("  │  PID │ T.Inicio│ T.Fin │ T.Retorno │ T.Espera│")
    print("  ├──────┼─────────┼───────┼───────────┼─────────┤")

    total_retorno = 0
    total_espera  = 0

    for r in resultados:
        print(f"  │  {r['pid']:<3} │   {r['inicio']:<5} │  {r['fin']:<4} │    {r['retorno']:<6} │   {r['espera']:<5} │")
        total_retorno += r["retorno"]
        total_espera  += r["espera"]

    n            = len(resultados)
    prom_retorno = total_retorno / n
    prom_espera  = total_espera  / n

    print("  ├──────┼─────────┼───────┼───────────┼─────────┤")
    print(f"  │ Prom │         │       │   {prom_retorno:<7.2f} │  {prom_espera:<6.2f} │")
    print("  └──────┴─────────┴───────┴───────────┴─────────┘")

    return prom_retorno, prom_espera


def imprimir_resumen(quantum, cambios_contexto, prom_retorno, prom_espera):
    imprimir_seccion("RESUMEN — ROUND ROBIN")
    print(f"  Quantum utilizado        : {quantum} ut")
    print(f"  Cambios de contexto      : {cambios_contexto}")
    print(f"  T. promedio de retorno   : {prom_retorno:.2f} ut")
    print(f"  T. promedio de espera    : {prom_espera:.2f} ut")
    print()
    print(SEP_DOBLE)
    print()


def round_robin(procesos, quantum):
    tabla = []
    for p in procesos:
        tabla.append({
            "pid"      : p["pid"],
            "llegada"  : p["llegada"],
            "ejecucion": p["ejecucion"],
            "restante" : p["ejecucion"],
            "inicio"   : -1,
            "fin"      : -1,
        })

    tabla.sort(key=lambda p: p["llegada"])

    cola: deque    = deque()
    gantt          = []
    cambios        = 0
    tiempo         = 0
    completados    = 0
    proceso_actual = None
    siguiente      = 0
    n              = len(tabla)

    while completados < n:
        while siguiente < n and tabla[siguiente]["llegada"] <= tiempo:
            cola.append(tabla[siguiente])
            siguiente += 1

        if not cola:
            gantt.append("--")
            tiempo += 1
            continue

        proceso = cola.popleft()

        if proceso_actual is not None and proceso_actual["pid"] != proceso["pid"]:
            cambios += 1
        proceso_actual = proceso

        if proceso["inicio"] == -1:
            proceso["inicio"] = tiempo

        turno = min(quantum, proceso["restante"])

        for _ in range(turno):
            gantt.append(proceso["pid"])
            tiempo += 1
            while siguiente < n and tabla[siguiente]["llegada"] <= tiempo:
                cola.append(tabla[siguiente])
                siguiente += 1

        proceso["restante"] -= turno

        if proceso["restante"] == 0:
            proceso["fin"] = tiempo
            completados += 1
        else:
            cola.append(proceso)

    resultados = []
    for p in tabla:
        retorno = p["fin"] - p["llegada"]
        espera  = retorno  - p["ejecucion"]
        resultados.append({
            "pid"    : p["pid"],
            "inicio" : p["inicio"],
            "fin"    : p["fin"],
            "retorno": retorno,
            "espera" : espera,
        })

    resultados.sort(key=lambda r: r["pid"])
    return gantt, resultados, cambios


def main():
    imprimir_encabezado()
    imprimir_tabla_procesos(PROCESOS_BASE)

    quantum = pedir_quantum()

    print()
    print("  Iniciando simulación...")
    time.sleep(0.8)

    gantt, resultados, cambios = round_robin(PROCESOS_BASE, quantum)

    imprimir_gantt(gantt, PROCESOS_BASE)
    prom_retorno, prom_espera = imprimir_tabla_resultados(resultados)
    imprimir_resumen(quantum, cambios, prom_retorno, prom_espera)


if __name__ == "__main__":
    main()
