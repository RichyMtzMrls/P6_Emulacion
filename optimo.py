import tkinter as tk
from tkinter import filedialog, messagebox
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
        return None

def reemplazo_optimo(demanda, num_frames):
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
                        distancia = (demanda[i+1:].index(f) + 1)
                        futuras.append(distancia)
                    else:
                        futuras.append(float('inf'))        
                reemplazar = futuras.index(max(futuras))
                frames[reemplazar] = pagina

        proximos = []

        for f in frames:
            if f == -1:
                proximos.append("-")
            elif f in demanda[i+1:]:
                distancia = (demanda[i+1:].index(f) + 1)
                proximos.append(distancia)
            else:
                proximos.append("-")
        historial.append(frames.copy())
        historial_pro.append(proximos.copy())
    return (historial, historial_pro, fallos, total_fallos)

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmo de Reemplazo de Página Óptimo")
        self.geometry("1400x750")
        self.config(bg="white")
        self.crear_interfaz()

    def crear_interfaz(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="x", pady=10)
        tk.Label(frame, text="Frames:", bg="white", font=("Arial", 12)).pack(side="left", padx=5)
        self.frames_var = tk.StringVar(value="4")
        tk.OptionMenu(frame,self.frames_var, "4","8").pack(side="left")
        tk.Label(frame, text="Tiempo:", bg="white", font=("Arial", 12)).pack(side="left", padx=10)
        self.entry_tiempo = tk.Entry(frame,width=8)
        self.entry_tiempo.insert(0, "25")
        self.entry_tiempo.pack(side="left")
        tk.Button(frame, text="Generar Aleatorio", bg="#d9ead3", width=18, command=self.generar_aleatorio).pack(side="left", padx=10)
        tk.Button(frame, text="Cargar TXT", bg="#cfe2f3", width=15, command=self.cargar_txt).pack(side="left", padx=10)
        tk.Button(frame, text="Ingreso Manual", bg="#fff2cc", width=15, command=self.ingreso_manual).pack(side="left", padx=10)
        tk.Button(frame, text="Regresar al Menú", bg="#ffcccc", width=15, command=self.destroy).pack(side="right", padx=10)
        frame_scroll = tk.Frame(self)
        frame_scroll.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(frame_scroll, bg="white")
        scroll_x = tk.Scrollbar(frame_scroll, orient="horizontal", command=self.canvas.xview)
        scroll_y = tk.Scrollbar(frame_scroll, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.label_fallos = tk.Label(self, text="", bg="white", fg="blue", font=("Arial", 16, "bold"))
        self.label_fallos.pack(pady=10)

    def generar_aleatorio(self):
        try:
            tiempo = int(self.entry_tiempo.get())
        except:
            messagebox.showerror("Error", "Tiempo inválido")
            return
        frames = int(self.frames_var.get())

        if frames == 4:
            procesos = 8
        else:
            procesos = 16
            
        demanda = generar_demanda(procesos,tiempo)
        self.mostrar_tabla(demanda, frames)

    def cargar_txt(self):
        ruta = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])

        if not ruta:
            return

        demanda = leer_desde_archivo(ruta)

        if demanda is None:
            messagebox.showerror("Error", "No se pudo leer el archivo")
            return

        frames = int(self.frames_var.get())
        self.mostrar_tabla(demanda,frames)

    def ingreso_manual(self):
        ventana = tk.Toplevel(self)
        ventana.title("Manual")
        ventana.geometry("500x200")
        tk.Label(ventana, text="Ingrese demanda separada por espacios:").pack(pady=10)
        entrada = tk.Entry(ventana,width=60)
        entrada.pack(pady=10)
        
        def procesar():
            try:
                demanda = [int(x)for x in entrada.get().split()]
                frames = int(self.frames_var.get())
                self.mostrar_tabla(demanda,frames)
                ventana.destroy()
            except:
                messagebox.showerror("Error", "Datos inválidos")

        tk.Button(ventana, text="Aceptar", command=procesar).pack(pady=10)

    def mostrar_tabla(self, demanda, num_frames):
        self.canvas.create_text(700, 35, text="ALGORITMO DE REEMPLAZO DE PÁGINA ÓPTIMO", font=("Arial", 18, "bold"), fill="black")
        (historial, pros, fallos,total_fallos) = reemplazo_optimo( demanda, num_frames)
        ancho_celda = 60
        alto_celda = 35
        borde = 1
        x_inicio = 100
        y_inicio = 100
        self.canvas.create_rectangle(0, y_inicio, x_inicio, y_inicio + alto_celda, fill="white", outline="black", width=borde)
        self.canvas.create_text(50, y_inicio + 18, text="Demanda", font=("Arial", 11, "bold"))

        for t in range(len(demanda)):
            x = x_inicio + (t * ancho_celda * 2)
            self.canvas.create_rectangle(x, y_inicio, x + ancho_celda, y_inicio + alto_celda, fill="white", outline="black", width=borde)
            self.canvas.create_text(x + 30, y_inicio + 18, text=str(demanda[t]), font=("Arial", 11, "bold"))

        y_fallo = y_inicio + alto_celda
        self.canvas.create_rectangle(0, y_fallo, x_inicio, y_fallo + alto_celda, fill="#f4cccc", outline="black", width=borde)
        self.canvas.create_text(50, y_fallo + 18, text="Fallo", font=("Arial", 10, "bold"))

        for t in range(len(fallos)):
            x = x_inicio + (t * ancho_celda * 2)
            self.canvas.create_rectangle(x, y_fallo, x + ancho_celda, y_fallo + alto_celda, fill="#fce5e5", outline="black", width=borde)
            self.canvas.create_text(x + 30, y_fallo + 18, text=fallos[t], fill="red", font=("Arial", 12, "bold"))

        y_frames = y_fallo + alto_celda

        for f in range(num_frames):
            y = y_frames + (f * alto_celda)
            self.canvas.create_rectangle(0, y, x_inicio, y + alto_celda, fill="#d9ead3", outline="black", width=borde)
            self.canvas.create_text(50, y + 18, text=f"F{f+1}", font=("Arial", 11, "bold"))

            for t in range(len(historial)):
                x = x_inicio + (t * ancho_celda * 2)
                valor = historial[t][f]
                pro = pros[t][f]
                texto = ("-"if valor == -1
                    else str(valor))
                self.canvas.create_rectangle(x, y, x + ancho_celda, y + alto_celda, fill="white", outline="black", width=borde)
                self.canvas.create_text(x + 30, y + 18, text=texto, font=("Arial", 11, "bold"))
                self.canvas.create_rectangle(x + ancho_celda, y_frames - alto_celda, x + (ancho_celda * 2), y_frames, fill="white", outline="black", width=borde)
                self.canvas.create_text(x + (ancho_celda * 1.5), y_frames - 18, text="Pro",font=("Arial", 9, "bold"))
                self.canvas.create_rectangle(x + ancho_celda, y, x + (ancho_celda * 2), y + alto_celda, fill="#fff2cc", outline="black", width=borde)
                self.canvas.create_text(x + (ancho_celda * 1.5), y + 18, text=str(pro), font=("Arial", 10, "bold"))

        y_tiempo = (y_frames +(num_frames * alto_celda))
        self.canvas.create_rectangle(0, y_tiempo, x_inicio, y_tiempo + alto_celda, fill="white", outline="black", width=borde)
        self.canvas.create_text(50, y_tiempo + 18, text="Tiempo", font=("Arial", 11, "bold"))

        for t in range(len(demanda)):
            x = x_inicio + (t * ancho_celda * 2)
            self.canvas.create_rectangle(x, y_tiempo, x + ancho_celda, y_tiempo + alto_celda, fill="white", outline="black", width=borde)
            self.canvas.create_text(x + 30, y_tiempo + 18, text=str(t + 1), font=("Arial", 11, "bold"))

        self.label_fallos.config(text=(f"TOTAL DE FALLOS DE PÁGINA: "f"{total_fallos}"))
        ancho_total = (x_inicio + (len(demanda) * ancho_celda * 2) + 100)
        alto_total = (y_tiempo + alto_celda + 100)
        self.canvas.config(scrollregion=(0, 0, ancho_total, alto_total))

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()