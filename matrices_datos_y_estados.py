import numpy as np
import pandas as pd
import csv
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox

def procesamiento_datos(n, m, muestras):
    EstadoCanalF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoCanalP = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoP = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoCanalF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    muestras_almacenadas = muestras.copy()

    for i in range(n):
        muestra = muestras[i]

        for j in range(m):
            EstadoCanalF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
            if j < m - 1:
                EstadoEstadoF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra[j + 1:])), 2)] += 1 / (n - (i == n-1))

        if i > 0:
            EstadoCanalF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n
            EstadoEstadoF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n

        for j in range(m):
            muestra_previa = muestra.copy()
            muestra_previa[j] = 1 - muestra_previa[j]
            EstadoCanalP[int(''.join(map(str, muestra_previa)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
        if i > 0:
            EstadoEstadoP[int(''.join(map(str, muestras[i - 1])), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))

    return (
        EstadoCanalF,
        EstadoEstadoF,
        EstadoCanalP,
        EstadoEstadoP,
        EstadoCanalF_aux,
        EstadoEstadoF_aux,
        muestras_almacenadas,
    )

def generar_entradas_aleatorias(n, m):
    muestras = []
    for i in range(n):
        muestra = np.random.randint(2, size=m)
        muestras.append(muestra)
    return muestras

class InterfazGrafica:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Procesamiento de Datos")

        self.muestras_almacenadas = None
        self.matrices = None

        self.n_label = ttk.Label(self.window, text="Número de muestras (n):")
        self.m_label = ttk.Label(self.window, text="Número de canales (m):")
        self.n_entry = ttk.Entry(self.window)
        self.m_entry = ttk.Entry(self.window)

        self.btn_manual = ttk.Button(self.window, text="Ingresar datos manualmente", command=self.ingresar_manualmente)
        self.btn_aleatorio = ttk.Button(self.window, text="Generar datos aleatorios", command=self.generar_aleatorios)
        self.btn_mostrar_canal_f = ttk.Button(self.window, text="Mostrar EstadoCanalF", command=self.mostrar_canal_f)
        self.btn_mostrar_estado_f = ttk.Button(self.window, text="Mostrar EstadoEstadoF", command=self.mostrar_estado_f)
        self.btn_mostrar_canal_p = ttk.Button(self.window, text="Mostrar EstadoCanalP", command=self.mostrar_canal_p)
        self.btn_mostrar_estado_p = ttk.Button(self.window, text="Mostrar EstadoEstadoP", command=self.mostrar_estado_p)
        self.btn_mostrar_aleatorio = ttk.Button(self.window, text="Mostrar Datos ", command=self.mostrar_datos)
        self.btn_cargar_csv = ttk.Button(self.window, text="Cargar desde CSV", command=self.cargar_csv)
        self.btn_salir = ttk.Button(self.window, text="Salir", command=self.window.quit)

        self.n_label.grid(row=0, column=0, pady=5, padx=5)
        self.n_entry.grid(row=0, column=1, pady=5, padx=5)
        self.m_label.grid(row=1, column=0, pady=5, padx=5)
        self.m_entry.grid(row=1, column=1, pady=5, padx=5)

        self.btn_manual.grid(row=2, column=0, columnspan=2, pady=5)
        self.btn_aleatorio.grid(row=3, column=0, columnspan=2, pady=5)
        self.btn_mostrar_canal_f.grid(row=4, column=0, columnspan=2, pady=5)
        self.btn_mostrar_estado_f.grid(row=5, column=0, columnspan=2, pady=5)
        self.btn_mostrar_canal_p.grid(row=6, column=0, columnspan=2, pady=5)
        self.btn_mostrar_estado_p.grid(row=7, column=0, columnspan=2, pady=5)
        self.btn_mostrar_aleatorio.grid(row=8, column=0, columnspan=2, pady=5)
        self.btn_cargar_csv.grid(row=9, column=0, columnspan=2, pady=5)
        self.btn_salir.grid(row=10, column=0, columnspan=2, pady=5)

    def ingresar_manualmente(self):
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            muestras = []
            for i in range(n):
                muestra_str = simpledialog.askstring(f"Ingresar datos manualmente", f"Ingrese la muestra {i + 1} como una cadena de {m} valores binarios:")
                muestra = [int(bit) for bit in muestra_str]
                muestras.append(muestra)
            self.matrices = procesamiento_datos(n, m, muestras)
            self.muestras_almacenadas = muestras
            messagebox.showinfo("Éxito", "Datos ingresados correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos.")

    def generar_aleatorios(self):
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            muestras = [np.random.randint(2, size=m) for _ in range(n)]
            muestras = [list(muestra) + [0] * (m - len(muestra)) for muestra in muestras]
            self.matrices = procesamiento_datos(n, m, muestras)
            self.muestras_almacenadas = muestras  # Actualiza muestras_almacenadas con los datos generados
            messagebox.showinfo("Éxito", "Datos aleatorios generados correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos.")


    def mostrar_canal_f(self):
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[0], "Matriz EstadoCanalF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_f(self):
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[1], "Matriz EstadoEstadoF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_canal_p(self):
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[2], "Matriz EstadoCanalP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_p(self):
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[3], "Matriz EstadoEstadoP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_datos(self):
        if self.muestras_almacenadas is not None:
            self.mostrar_matriz_datos(self.muestras_almacenadas)
        else:
            messagebox.showwarning("Advertencia", "No hay datos generados aleatoriamente.")

    def cargar_csv(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
        if archivo:
            try:
                with open(archivo, newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    muestras = []
                    for row in reader:
                        muestra = [int(bit) for bit in row]
                        muestras.append(muestra)
                    n = len(muestras)
                    m = len(muestras[0])
                    self.matrices = procesamiento_datos(n, m, muestras)
                    self.muestras_almacenadas = muestras
                    messagebox.showinfo("Éxito", "Datos cargados desde CSV correctamente.")
            except FileNotFoundError:
                messagebox.showerror("Error", "Archivo no encontrado.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo CSV: {str(e)}")

    def mostrar_matriz(self, matriz, titulo):
        df = pd.DataFrame(matriz, columns=[f'Estado {i}' for i in range(matriz.shape[1])])
        self.mostrar_dataframe(df, titulo)

    def mostrar_matriz_datos(self, muestras):
        max_len = max(len(muestra) for muestra in muestras)

        # Asegúrate de que todas las muestras tengan la misma longitud
        if not all(len(muestra) == max_len for muestra in muestras):
            print("Longitudes de las muestras:", [len(muestra) for muestra in muestras])
            messagebox.showerror("Error", "Las muestras generadas aleatoriamente tienen longitudes diferentes.")
            return

        muestras_rellenadas = [muestra + [0] * (max_len - len(muestra)) for muestra in muestras]

        df = pd.DataFrame(muestras_rellenadas, columns=[f'Canal {i + 1}' for i in range(max_len)])
        
        self.mostrar_dataframe(df, "Matriz de Datos")


    def mostrar_dataframe(self, df, titulo):
        top = tk.Toplevel(self.window)
        top.title(titulo)
        table = ttk.Treeview(top)
        table['columns'] = list(df.columns)
        column_width = 75
        for column in df.columns:
            table.column(column, width=column_width, anchor='w')
            table.heading(column, text=column, anchor='w')
        for index, row in df.iterrows():
            table.insert("", index, values=list(row))
        table.pack()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    interfaz = InterfazGrafica()
    interfaz.run()