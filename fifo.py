import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

class Proceso:
    def __init__(self, nombre, llegada, ejecucion):
        self.nombre = nombre
        self.llegada = llegada
        self.ejecucion = ejecucion
        self.restante = ejecucion
        self.comienzo = -1
        self.fin_real = 0
        self.retorno = 0
        self.espera = 0

class PlanificadorFIFO:
    def __init__(self, procesos):
        self.procesos = sorted(procesos, key=lambda p: p.llegada)
        self.tiempo_maximo = 0
        self.historial_estados = {p.nombre: [] for p in self.procesos}
        self.historial_cola = []  
        self.simular()

    def simular(self):
        tiempo = 0
        completados = 0
        n = len(self.procesos)
        cola = []
        cpu = None

        while completados < n:
            for p in self.procesos:
                if p.llegada == tiempo:
                    cola.append(p)

            if cpu and cpu.restante == 0:
                cpu.fin_real = tiempo
                cpu.retorno = cpu.fin_real - cpu.llegada
                cpu.espera = cpu.retorno - cpu.ejecucion
                self.historial_estados[cpu.nombre].append('F')
                completados += 1
                cpu = None
            elif cpu:
                self.historial_estados[cpu.nombre].append('E')

            if not cpu and cola:
                cpu = cola.pop(0)
                if cpu.comienzo == -1:
                    cpu.comienzo = tiempo
                self.historial_estados[cpu.nombre].append('E')

            estado_cola_actual = []
            for p in reversed(cola):
                self.historial_estados[p.nombre].append('L')
                estado_cola_actual.append(p.nombre)
            
            self.historial_cola.append(estado_cola_actual)

            for p in self.procesos:
                if p != cpu and p not in cola:
                    if len(self.historial_estados[p.nombre]) <= tiempo:
                         self.historial_estados[p.nombre].append('')

            if cpu:
                cpu.restante -= 1
                
            tiempo += 1

        self.tiempo_maximo = tiempo

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador FIFO (FCFS) - Sistemas Operativos")
        self.geometry("1100x700")
        self.configure(bg="#f0f0f0")
        self.crear_interfaz()

    def crear_interfaz(self):
        frame_controles = tk.Frame(self, bg="#f0f0f0", pady=10)
        frame_controles.pack(fill=tk.X)

        tk.Button(frame_controles, text="Cargar desde .txt", command=self.cargar_txt, width=18).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_controles, text="Ingreso Manual", command=self.abrir_ingreso_manual, width=18).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_controles, text="Generar Aleatorios", command=self.generar_aleatorios, width=18).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_controles, text="Regresar al Menú", bg="#ffcccc", width=18, command=self.destroy).pack(side=tk.RIGHT, padx=10)

        columnas = ("Proceso", "T. Ejecución", "T. Llegada", "T. Comienzo", "T. Fin", "T. Retorno", "T. Espera")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=10)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=100)
        self.tree.pack(fill=tk.X, padx=20, pady=10)
        
        self.lbl_promedios = tk.Label(self, text="T. Medio Retorno: 0.00 | T. Medio Espera: 0.00", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.lbl_promedios.pack()
        
        frame_gantt = tk.Frame(self)
        frame_gantt.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(frame_gantt, bg="white")
        scrollbar_x = ttk.Scrollbar(frame_gantt, orient="horizontal", command=self.canvas.xview)
        scrollbar_y = ttk.Scrollbar(frame_gantt, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def cargar_txt(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo de procesos",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        procesos = []
        try:
            with open(ruta, 'r') as archivo:
                for i, linea in enumerate(archivo):
                    linea = linea.strip()
                    if not linea or linea.startswith('#'):
                        continue
                    partes = linea.split(',')
                    if len(partes) != 2:
                        messagebox.showerror("Error de Formato", f"Error en la línea {i+1}: Debe ser 'Llegada, Ejecución'.")
                        return
                    llegada = int(partes[0].strip())
                    ejecucion = int(partes[1].strip())
                    nombre = chr(65 + len(procesos)) 
                    procesos.append(Proceso(nombre, llegada, ejecucion))
            
            if procesos:
                self.ejecutar_simulacion(procesos)
                messagebox.showinfo("Éxito", f"Se cargaron {len(procesos)} procesos correctamente.")
            else:
                messagebox.showwarning("Advertencia", "El archivo está vacío o no contiene datos válidos.")
                
        except ValueError:
            messagebox.showerror("Error de Datos", "El archivo contiene caracteres no numéricos donde se esperaban números.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def abrir_ingreso_manual(self):
        ventana_manual = tk.Toplevel(self)
        ventana_manual.title("Ingreso Manual de Procesos")
        ventana_manual.geometry("350x450")
        ventana_manual.transient(self) 
        ventana_manual.grab_set() 

        tk.Label(ventana_manual, text="Ingresa T. Llegada y T. Ejecución", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        tk.Label(ventana_manual, text="Proceso").grid(row=1, column=0)
        tk.Label(ventana_manual, text="Llegada").grid(row=1, column=1)
        tk.Label(ventana_manual, text="Ejecución").grid(row=1, column=2)

        entradas_llegada = []
        entradas_ejecucion = []

        for i in range(10):
            nombre = chr(65 + i)
            tk.Label(ventana_manual, text=f"{nombre}:").grid(row=i+2, column=0, padx=10, pady=2)
            
            ent_llegada = ttk.Entry(ventana_manual, width=10)
            ent_llegada.grid(row=i+2, column=1, padx=5)
            entradas_llegada.append(ent_llegada)
            
            ent_ejec = ttk.Entry(ventana_manual, width=10)
            ent_ejec.grid(row=i+2, column=2, padx=5)
            entradas_ejecucion.append(ent_ejec)

        def procesar_manual():
            procesos = []
            for i in range(10):
                llegada_str = entradas_llegada[i].get()
                ejecucion_str = entradas_ejecucion[i].get()
                
                if not llegada_str and not ejecucion_str:
                    continue
                    
                try:
                    llegada = int(llegada_str)
                    ejecucion = int(ejecucion_str)
                    if ejecucion <= 0:
                        raise ValueError("La ejecución debe ser mayor a 0.")
                    procesos.append(Proceso(chr(65 + len(procesos)), llegada, ejecucion))
                except ValueError:
                    messagebox.showerror("Error", f"Datos inválidos en la fila {chr(65+i)}.\nAsegúrate de usar números enteros.")
                    return
            
            if procesos:
                self.ejecutar_simulacion(procesos)
                ventana_manual.destroy()
            else:
                messagebox.showwarning("Advertencia", "Debes ingresar al menos un proceso.")

        ttk.Button(ventana_manual, text="Simular", command=procesar_manual).grid(row=13, column=0, columnspan=3, pady=20)

    def generar_aleatorios(self):
        nombres = [chr(65 + i) for i in range(10)]
        procesos = [Proceso(nombres[i], random.randint(0, 15), random.randint(2, 10)) for i in range(10)]
        self.ejecutar_simulacion(procesos)

    def ejecutar_simulacion(self, procesos):
        sim = PlanificadorFIFO(procesos)
        
        for fila in self.tree.get_children():
            self.tree.delete(fila)

        suma_retorno = 0
        suma_espera = 0

        for p in sorted(sim.procesos, key=lambda x: x.nombre):
            t_fin_display = p.fin_real - 1 
            self.tree.insert("", tk.END, values=(
                p.nombre, p.ejecucion, p.llegada, p.comienzo, t_fin_display, p.retorno, p.espera
            ))
            suma_retorno += p.retorno
            suma_espera += p.espera

        n = len(procesos)
        self.lbl_promedios.config(text=f"T. Medio Retorno: {suma_retorno/n:.2f}  |  T. Medio Espera: {suma_espera/n:.2f}")

        self.dibujar_gantt(sim)

    def dibujar_gantt(self, sim):
        self.canvas.delete("all")
        
        celda_w = 25
        celda_h = 25
        margen_x = 50
        margen_y = 150 
        
        max_t = sim.tiempo_maximo
        procesos_ordenados = sorted(sim.procesos, key=lambda x: x.nombre)
        
        color_e = "#d9ead3" 
        color_l = "#fff2cc" 
        color_f = "#f4cccc" 

        for t in range(max_t):
            x = margen_x + (t * celda_w)
            self.canvas.create_text(x + celda_w/2, margen_y - 10, text=str(t), font=("Arial", 8, "bold"))

        self.canvas.create_text(margen_x/2, margen_y - 30, text="Cola", font=("Arial", 10, "bold"))
        for t, estado_cola in enumerate(sim.historial_cola):
            x = margen_x + (t * celda_w)
            for nivel, texto_proceso in enumerate(estado_cola):
                y = margen_y - 25 - (nivel * celda_h)
                self.canvas.create_rectangle(x, y - celda_h, x + celda_w, y, fill="#cfe2f3", outline="gray")
                self.canvas.create_text(x + celda_w/2, y - celda_h/2, text=texto_proceso, font=("Arial", 8, "bold"))

        for i, p in enumerate(procesos_ordenados):
            y = margen_y + (i * celda_h)
            self.canvas.create_text(margen_x/2, y + celda_h/2, text=p.nombre, font=("Arial", 10, "bold"))
            estados = sim.historial_estados[p.nombre]
            
            for t in range(max_t):
                x = margen_x + (t * celda_w)
                estado = estados[t] if t < len(estados) else ""
                
                color_fondo = "white"
                if estado == 'E': color_fondo = color_e
                elif estado == 'L': color_fondo = color_l
                elif estado == 'F': color_fondo = color_f

                self.canvas.create_rectangle(x, y, x + celda_w, y + celda_h, fill=color_fondo, outline="gray")
                
                if estado:
                    color_texto = "green" if estado == 'E' else "red" if estado == 'F' else "black"
                    self.canvas.create_text(x + celda_w/2, y + celda_h/2, text=estado, fill=color_texto, font=("Arial", 9, "bold"))

        ancho_total = margen_x + (max_t * celda_w) + 50
        alto_total = margen_y + (len(procesos_ordenados) * celda_h) + 50
        self.canvas.config(scrollregion=(0, 0, ancho_total, alto_total))

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()