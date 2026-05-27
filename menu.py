import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import random
import copy

class Comparador:
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

    @staticmethod
    def generar_demanda():
        return [random.randint(1, 8) for _ in range(25)]

    @staticmethod
    def simular_fifo(procesos):
        procesos_copia = [p.copy() for p in procesos]
        procesos_copia.sort(key=lambda p: p["llegada"])
        tiempo = 0
        espera_total, retorno_total = 0, 0
        for p in procesos_copia:
            if tiempo < p["llegada"]: tiempo = p["llegada"]
            espera = tiempo - p["llegada"]
            tiempo += p["ejecucion"]
            retorno = tiempo - p["llegada"]
            espera_total += espera
            retorno_total += retorno
        n = len(procesos_copia)
        return retorno_total / n, espera_total / n

    @staticmethod
    def simular_sjf(procesos):
        procesos_copia = [p.copy() for p in procesos]
        procesos_copia.sort(key=lambda p: p["llegada"])
        tiempo, completados = 0, 0
        espera_total, retorno_total = 0, 0
        cola = []
        restantes = procesos_copia
        
        while completados < len(procesos_copia):
            cola.extend([p for p in restantes if p["llegada"] <= tiempo])
            restantes = [p for p in restantes if p["llegada"] > tiempo]
            
            if cola:
                cola.sort(key=lambda p: p["ejecucion"])
                p_actual = cola.pop(0)
                if tiempo < p_actual["llegada"]: tiempo = p_actual["llegada"]
                espera = tiempo - p_actual["llegada"]
                tiempo += p_actual["ejecucion"]
                retorno = tiempo - p_actual["llegada"]
                espera_total += espera
                retorno_total += retorno
                completados += 1
            else:
                tiempo += 1
        n = len(procesos_copia)
        return retorno_total / n, espera_total / n

    @staticmethod
    def simular_rr(procesos, quantum=3):
        from collections import deque
        tabla = [p.copy() for p in procesos]
        for p in tabla:
            p["restante"] = p["ejecucion"]
            p["inicio"] = -1
        
        tabla.sort(key=lambda p: p["llegada"])
        cola = deque()
        tiempo, completados, siguiente = 0, 0, 0
        espera_total, retorno_total = 0, 0
        n = len(tabla)

        while completados < n:
            while siguiente < n and tabla[siguiente]["llegada"] <= tiempo:
                cola.append(tabla[siguiente])
                siguiente += 1
            if not cola:
                tiempo += 1
                continue
            
            p = cola.popleft()
            if p["inicio"] == -1: p["inicio"] = tiempo
            turno = min(quantum, p["restante"])
            tiempo += turno
            p["restante"] -= turno
            
            while siguiente < n and tabla[siguiente]["llegada"] <= tiempo:
                cola.append(tabla[siguiente])
                siguiente += 1
                
            if p["restante"] == 0:
                retorno = tiempo - p["llegada"]
                espera = retorno - p["ejecucion"]
                retorno_total += retorno
                espera_total += espera
                completados += 1
            else:
                cola.append(p)
        return retorno_total / n, espera_total / n

    @staticmethod
    def simular_optimo(demanda, num_frames=4):
        frames = [-1] * num_frames
        total_fallos = 0
        for i in range(len(demanda)):
            pagina = demanda[i]
            if pagina not in frames:
                total_fallos += 1
                if -1 in frames:
                    indice = frames.index(-1)
                    frames[indice] = pagina
                else:
                    futuras = []
                    for f in frames:
                        if f in demanda[i+1:]:
                            futuras.append(demanda[i+1:].index(f) + 1)
                        else:
                            futuras.append(float('inf'))        
                    frames[futuras.index(max(futuras))] = pagina
        return total_fallos

class MenuPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto Emulación - Sistemas Operativos 3")
        self.geometry("600x550")
        self.configure(bg="#2c3e50")
        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self, text="MENÚ PRINCIPAL DE EMULACIÓN", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(pady=30)
        frame_botones = tk.Frame(self, bg="#2c3e50")
        frame_botones.pack(pady=10)
        estilo_btn = {"font": ("Arial", 12, "bold"), "width": 30, "pady": 10, "bg": "#ecf0f1", "cursor": "hand2"}

        tk.Button(frame_botones, text="1. Simulación FIFO", command=lambda: self.abrir_programa("fifo.py"), **estilo_btn).pack(pady=10)
        tk.Button(frame_botones, text="2. Simulación SJF", command=lambda: self.abrir_programa("sjf.py"), **estilo_btn).pack(pady=10)
        tk.Button(frame_botones, text="3. Simulación Round Robin", command=lambda: self.abrir_programa("rr.py"), **estilo_btn).pack(pady=10)
        tk.Button(frame_botones, text="4. Algoritmo Óptimo (Paginación)", command=lambda: self.abrir_programa("optimo.py"), **estilo_btn).pack(pady=10)
        tk.Button(frame_botones, text="📊 Comparar 2 Algoritmos", command=self.abrir_seleccion_comparativa, font=("Arial", 12, "bold"), width=30, pady=10, bg="#f39c12", fg="white", cursor="hand2").pack(pady=20)

    def abrir_programa(self, script_name):
        try:
            self.withdraw()
            subprocess.run(["python3", script_name])
            self.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir {script_name}.\nError: {e}")
            self.deiconify()

    def abrir_seleccion_comparativa(self):
        self.ventana_sel = tk.Toplevel(self)
        self.ventana_sel.title("Seleccionar Algoritmos")
        self.ventana_sel.geometry("350x280")
        self.ventana_sel.configure(bg="#ecf0f1")
        self.ventana_sel.grab_set()

        tk.Label(self.ventana_sel, text="Elige exactamente 2 algoritmos:", font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=15)

        self.opciones_vars = {
            "FIFO (FCFS)": tk.BooleanVar(),
            "SJF": tk.BooleanVar(),
            "Round Robin (Q=3)": tk.BooleanVar(),
            "Óptimo (Paginación)": tk.BooleanVar()
        }

        frame_checks = tk.Frame(self.ventana_sel, bg="#ecf0f1")
        frame_checks.pack(pady=5)

        for texto, var in self.opciones_vars.items():
            tk.Checkbutton(frame_checks, text=texto, variable=var, font=("Arial", 11), bg="#ecf0f1").pack(anchor=tk.W, pady=2)

        tk.Button(self.ventana_sel, text="Iniciar Comparación", command=self.procesar_seleccion, bg="#3498db", fg="white", font=("Arial", 11, "bold")).pack(pady=20)

    def procesar_seleccion(self):
        seleccionados = [nombre for nombre, var in self.opciones_vars.items() if var.get()]
        if len(seleccionados) != 2:
            messagebox.showwarning("Atención", "Debes seleccionar exactamente 2 algoritmos.")
            return

        self.ventana_sel.destroy()

        if "Round Robin (Q=3)" in seleccionados:
            procesos = copy.deepcopy(Comparador.PROCESOS_BASE)
            demanda = Comparador.generar_demanda()
            self.mostrar_tabla_comparativa(procesos, demanda, seleccionados)
        else:
            self.abrir_ingreso_manual(seleccionados)

    def abrir_ingreso_manual(self, seleccionados):
        v_manual = tk.Toplevel(self)
        v_manual.title("Asignar Valores Manualmente")
        v_manual.geometry("380x500")
        v_manual.grab_set()

        necesita_cpu = "FIFO (FCFS)" in seleccionados or "SJF" in seleccionados
        necesita_optimo = "Óptimo (Paginación)" in seleccionados

        fila = 0
        entradas_ll = []
        entradas_ej = []
        ent_demanda = None

        if necesita_cpu:
            tk.Label(v_manual, text="Ingresa T. Llegada y T. Ejecución:", font=("Arial", 10, "bold")).grid(row=fila, column=0, columnspan=3, pady=5)
            fila += 1
            tk.Label(v_manual, text="Proceso").grid(row=fila, column=0)
            tk.Label(v_manual, text="Llegada").grid(row=fila, column=1)
            tk.Label(v_manual, text="Ejecución").grid(row=fila, column=2)
            fila += 1

            for i in range(10):
                tk.Label(v_manual, text=f"P{i}:").grid(row=fila, column=0, padx=5, pady=2)
                ell = ttk.Entry(v_manual, width=10)
                ell.grid(row=fila, column=1)
                eej = ttk.Entry(v_manual, width=10)
                eej.grid(row=fila, column=2)
                entradas_ll.append(ell)
                entradas_ej.append(eej)
                fila += 1

        if necesita_optimo:
            tk.Label(v_manual, text="Demanda (separada por espacios):", font=("Arial", 10, "bold")).grid(row=fila, column=0, columnspan=3, pady=10)
            fila += 1
            ent_demanda = ttk.Entry(v_manual, width=35)
            ent_demanda.grid(row=fila, column=0, columnspan=3)
            fila += 1

        def confirmar_datos():
            procesos_nuevos = []
            demanda_nueva = []

            if necesita_cpu:
                for i in range(10):
                    l_str = entradas_ll[i].get()
                    e_str = entradas_ej[i].get()
                    if not l_str and not e_str: continue
                    try:
                        procesos_nuevos.append({"pid": f"P{i}", "llegada": int(l_str), "ejecucion": int(e_str)})
                    except:
                        messagebox.showerror("Error", f"Valores inválidos en P{i}")
                        return
                if not procesos_nuevos:
                    messagebox.showwarning("Atención", "Ingresa al menos 1 proceso.")
                    return

            if necesita_optimo:
                d_str = ent_demanda.get()
                if not d_str.strip():
                    messagebox.showwarning("Atención", "Ingresa la secuencia de demanda.")
                    return
                try:
                    demanda_nueva = [int(x) for x in d_str.split()]
                except:
                    messagebox.showerror("Error", "La demanda solo debe contener números separados por espacio.")
                    return

            v_manual.destroy()
            self.mostrar_tabla_comparativa(procesos_nuevos, demanda_nueva, seleccionados)

        tk.Button(v_manual, text="Simular Comparación", command=confirmar_datos, bg="#2ecc71", fg="white", font=("Arial", 10, "bold")).grid(row=fila, column=0, columnspan=3, pady=20)

    def mostrar_tabla_comparativa(self, procesos_base, demanda_base, seleccionados):
        ventana_comp = tk.Toplevel(self)
        ventana_comp.title("Comparación Directa")
        ventana_comp.geometry("750x300")
        ventana_comp.configure(bg="#f0f0f0")
        ventana_comp.grab_set()

        titulo = "Comparativa usando datos de Round Robin" if "Round Robin (Q=3)" in seleccionados else "Comparativa con datos ingresados"
        tk.Label(ventana_comp, text=titulo, font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=15)

        columnas = ("Algoritmo", "T. Medio Retorno", "T. Medio Espera", "Fallos de Página")
        tree = ttk.Treeview(ventana_comp, columns=columnas, show="headings", height=3)
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=150)
        tree.pack(fill=tk.X, padx=20, pady=10)

        for alg in seleccionados:
            if alg == "FIFO (FCFS)":
                ret, esp = Comparador.simular_fifo(procesos_base)
                tree.insert("", tk.END, values=(alg, f"{ret:.2f}", f"{esp:.2f}", "N/A"))
            elif alg == "SJF":
                ret, esp = Comparador.simular_sjf(procesos_base)
                tree.insert("", tk.END, values=(alg, f"{ret:.2f}", f"{esp:.2f}", "N/A"))
            elif alg == "Round Robin (Q=3)":
                ret, esp = Comparador.simular_rr(procesos_base, quantum=3)
                tree.insert("", tk.END, values=(alg, f"{ret:.2f}", f"{esp:.2f}", "N/A"))
            elif alg == "Óptimo (Paginación)":
                fallos = Comparador.simular_optimo(demanda_base, num_frames=4)
                tree.insert("", tk.END, values=(alg, "N/A", "N/A", f"{fallos}"))

        tk.Button(ventana_comp, text="Cerrar", command=ventana_comp.destroy, bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()