import random
import os
import matplotlib.pyplot as plt

class Proceso:
    def __init__(self, pid, llegada, ejecucion):
        self.pid = pid
        self.llegada = llegada
        self.ejecucion = ejecucion
        self.restante = ejecucion
        self.inicio = -1
        self.fin = 0
        self.retorno = 0
        self.espera = 0
        self.estado = "Nuevo"

def obtener_tiempo_simulacion():
    while True:
        try:
            t = int(input("\nIngresa el tiempo de duración de la simulación (10 - 70): "))
            if 10 <= t <= 70:
                return t
            print("Error: El valor debe estar estrictamente entre 10 y 70.")
        except ValueError:
            print("Error: Por favor, ingresa un número entero válido.")

def cargar_desde_archivo():
    ruta = input("Ingresa el nombre del archivo (ej. procesos.txt): ")
    procesos = []
    if not os.path.exists(ruta):
        print(f"Error: No se encontró el archivo '{ruta}'.")
        return None
    
    try:
        with open(ruta, 'r') as archivo:
            for i, linea in enumerate(archivo):
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue # Ignorar líneas vacías o comentarios
                partes = linea.split(',')
                if len(partes) != 2:
                    print(f"Error en la línea {i+1}: Formato incorrecto. Debe ser 'Llegada, Ejecución'.")
                    return None
                llegada = int(partes[0].strip())
                ejecucion = int(partes[1].strip())
                procesos.append(Proceso(len(procesos) + 1, llegada, ejecucion))
        print(f"¡Se cargaron {len(procesos)} procesos desde el archivo!")
        return procesos
    except ValueError:
        print("Error: El archivo contiene caracteres no numéricos donde se esperaban números.")
        return None

def cargar_manualmente(num_procesos=10):
    procesos = []
    print(f"\n--- Ingreso Manual de {num_procesos} Procesos ---")
    for i in range(num_procesos):
        while True:
            try:
                entrada = input(f"Proceso {i+1} -> Ingresa 'Llegada, Ejecución' (ej. 2, 5): ")
                partes = entrada.split(',')
                if len(partes) != 2:
                    print("Formato incorrecto. Usa una coma para separar.")
                    continue
                llegada = int(partes[0].strip())
                ejecucion = int(partes[1].strip())
                procesos.append(Proceso(i+1, llegada, ejecucion))
                break
            except ValueError:
                print("Error: Debes ingresar números enteros válidos.")
    return procesos

def cargar_aleatorio(num_procesos=10):
    procesos = []
    for i in range(num_procesos):
        llegada = random.randint(0, 15)
        ejecucion = random.randint(2, 8)
        procesos.append(Proceso(i+1, llegada, ejecucion))
    print(f"¡Se generaron {num_procesos} procesos aleatorios!")
    return procesos

def menu_origen_datos():
    while True:
        print("\n--- MENÚ DE CARGA DE PROCESOS ---")
        print("1. Cargar desde archivo .txt")
        print("2. Ingresar datos manualmente (10 procesos)")
        print("3. Generar aleatoriamente (10 procesos)")
        opcion = input("Selecciona una opción (1-3): ")

        if opcion == '1':
            procesos = cargar_desde_archivo()
            if procesos: return procesos
        elif opcion == '2':
            return cargar_manualmente(10)
        elif opcion == '3':
            return cargar_aleatorio(10)
        else:
            print("Opción no válida. Intenta de nuevo.")

def graficar_gantt(registro, tiempo_maximo, total_procesos):
    fig, gnt = plt.subplots(figsize=(10, 5))
    gnt.set_title(f"Diagrama de Gantt - SJF (Simulación: {tiempo_maximo} u.t.)")
    gnt.set_xlabel("Unidades de Tiempo")
    gnt.set_ylabel("Procesos")
    
    gnt.set_xlim(0, tiempo_maximo)
    gnt.set_yticks([i * 10 + 5 for i in range(total_procesos)])
    
    # Asegurar que las etiquetas coincidan con los PIDs reales de los procesos graficados
    pids_graficados = sorted(list(set([p.pid for p in registro])))
    # Si no hay procesos, evitar error
    if not pids_graficados:
        pids_graficados = [1]
        
    gnt.set_yticklabels([f"P{pid}" for pid in pids_graficados] if pids_graficados else ["P1"])
    gnt.grid(True)

    # Crear un mapeo de PID a índice de fila para la gráfica
    pid_a_indice = {pid: i for i, pid in enumerate(pids_graficados)}

    for p in registro:
        idx = pid_a_indice[p.pid]
        if p.inicio > p.llegada:
            gnt.broken_barh([(p.llegada, p.inicio - p.llegada)], (idx * 10, 9), facecolors=('tab:red'))
        
        duracion_real = p.fin - p.inicio
        gnt.broken_barh([(p.inicio, duracion_real)], (idx * 10, 9), facecolors=('tab:blue'))

    from matplotlib.patches import Patch
    leyenda = [Patch(facecolor='tab:red', label='Espera'),
               Patch(facecolor='tab:blue', label='Ejecución')]
    gnt.legend(handles=leyenda)

    plt.tight_layout()
    plt.show()

def simular_sjf_no_apropiativo(procesos, tiempo_maximo):
    procesos.sort(key=lambda p: p.llegada)
    num_procesos = len(procesos)
    
    tiempo = 0
    completados = 0
    cola_listos = []
    proceso_actual = None
    procesos_finalizados = []
    registro_gantt = []

    print(f"\n{'Tiempo':<8} | {'Eventos':<40} | {'Estado General'}")
    print("-" * 85)

    while tiempo < tiempo_maximo and completados < num_procesos:
        eventos_tick = []

        for p in procesos:
            if p.llegada == tiempo and p.estado == "Nuevo":
                p.estado = "Espera"
                cola_listos.append(p)
                eventos_tick.append(f"P{p.pid} llega")

        if proceso_actual and proceso_actual.restante == 0:
            proceso_actual.estado = "Finalizado"
            proceso_actual.fin = tiempo
            proceso_actual.retorno = proceso_actual.fin - proceso_actual.llegada
            proceso_actual.espera = proceso_actual.retorno - proceso_actual.ejecucion
            procesos_finalizados.append(proceso_actual)
            registro_gantt.append(proceso_actual)
            eventos_tick.append(f"P{proceso_actual.pid} finaliza")
            completados += 1
            proceso_actual = None

        if not proceso_actual and cola_listos:
            cola_listos.sort(key=lambda p: p.ejecucion)
            proceso_actual = cola_listos.pop(0)
            proceso_actual.estado = "Ejecución"
            if proceso_actual.inicio == -1:
                proceso_actual.inicio = tiempo
            eventos_tick.append(f"P{proceso_actual.pid} a CPU")

        if eventos_tick:
            estados_str = ", ".join([f"P{p.pid}:{p.estado[:3]}" for p in procesos if p.estado not in ("Nuevo", "Finalizado")])
            print(f"{tiempo:<8} | {', '.join(eventos_tick):<40} | {estados_str}")

        if proceso_actual:
            proceso_actual.restante -= 1
        
        tiempo += 1

    if proceso_actual and tiempo == tiempo_maximo:
        proceso_actual.fin = tiempo
        registro_gantt.append(proceso_actual)
        print(f"{tiempo:<8} | Simulación terminada por límite. P{proceso_actual.pid} interrumpido.")

    print("\n--- Tabla Final de Tiempos (Procesos Completados) ---")
    print(f"{'PID':<5} | {'Llegada':<8} | {'Ejecución':<10} | {'Inicio':<8} | {'Fin':<5} | {'Retorno':<8} | {'Espera':<8}")
    for p in sorted(procesos_finalizados, key=lambda x: x.pid):
        print(f"{p.pid:<5} | {p.llegada:<8} | {p.ejecucion:<10} | {p.inicio:<8} | {p.fin:<5} | {p.retorno:<8} | {p.espera:<8}")

    if procesos_finalizados:
        prom_espera = sum(p.espera for p in procesos_finalizados) / len(procesos_finalizados)
        prom_retorno = sum(p.retorno for p in procesos_finalizados) / len(procesos_finalizados)
        print(f"\nT. Promedio Espera:  {prom_espera:.2f}")
        print(f"T. Promedio Retorno: {prom_retorno:.2f}")
    else:
        print("\nNingún proceso logró terminar en el tiempo dado.")

    if registro_gantt:
        graficar_gantt(registro_gantt, tiempo_maximo, len(set([p.pid for p in registro_gantt])))

if __name__ == '__main__':
    # 1. Seleccionar la fuente de datos
    lista_procesos = menu_origen_datos()
    
    # 2. Solicitar el tiempo límite
    t_maximo = obtener_tiempo_simulacion()
    
    # 3. Correr la simulación
    simular_sjf_no_apropiativo(lista_procesos, t_maximo)