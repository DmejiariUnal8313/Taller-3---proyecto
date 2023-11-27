# Importación de librerías necesarias
import numpy as np
import pandas as pd
import csv
import tkinter as tk
from prettytable import PrettyTable
from tkinter import ttk, simpledialog, filedialog, messagebox

# Función para procesar los datos y calcular diversas matrices de transición
def procesamiento_datos(n, m, muestras):
    """
    Calcula las matrices de transición para el canal y el estado a partir de las muestras dadas.

    Parameters:
        n (int): Número de muestras.
        m (int): Número de canales.
        muestras (list): Lista de muestras, donde cada muestra es una lista de bits.

    Returns:
        tuple: Tupla con las matrices de transición y las muestras originales.
    """
    # Matrices de transición para el canal y el estado
    EstadoCanalF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoCanalP = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoP = np.zeros((2 ** m, 2 ** m), dtype=float)
    
    # Matrices auxiliares para el cálculo del estado futuro
    EstadoCanalF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    EstadoEstadoF_aux = np.zeros((2 ** m, 2 ** m), dtype=float)
    
    # Copia de las muestras para mantener los datos originales
    muestras_almacenadas = muestras.copy()

    # Bucle sobre las muestras
    for i in range(n):
        muestra = muestras[i]

        # Actualización de matrices de transición para el canal y el estado
        for j in range(m):
            EstadoCanalF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
            if j < m - 1:
                EstadoEstadoF[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra[j + 1:])), 2)] += 1 / (n - (i == n-1))

        # Actualización de matrices auxiliares
        if i > 0:
            EstadoCanalF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n
            EstadoEstadoF_aux[int(''.join(map(str, muestra)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / n

        # Actualización de matrices de transición para el estado pasado
        for j in range(m):
            muestra_previa = muestra.copy()
            muestra_previa[j] = 1 - muestra_previa[j]
            EstadoCanalP[int(''.join(map(str, muestra_previa)), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))
        if i > 0:
            EstadoEstadoP[int(''.join(map(str, muestras[i - 1])), 2)][int(''.join(map(str, muestra)), 2)] += 1 / (n - (i == n-1))

    # Devuelve las matrices calculadas y las muestras originales
    return (
        EstadoCanalF,
        EstadoEstadoF,
        EstadoCanalP,
        EstadoEstadoP,
        EstadoCanalF_aux,
        EstadoEstadoF_aux,
        muestras_almacenadas,
    )

# Función para marginalizar una matriz dado un conjunto de índices
def marginalizar(matriz, indices):
    """
    Realiza la marginalización de una matriz dado un conjunto de índices.

    Parameters:
        matriz (np.ndarray): Matriz a marginalizar.
        indices (list): Lista de índices de columnas a marginalizar.

    Returns:
        np.ndarray: Matriz marginalizada.
    """
    return np.sum(matriz[:, indices], axis=1)

# Función para normalizar una matriz
def normalizar(matriz):
    """
    Normaliza una matriz dividiendo cada fila por la suma de sus elementos.

    Parameters:
        matriz (np.ndarray): Matriz a normalizar.

    Returns:
        np.ndarray: Matriz normalizada.
    """
    suma_filas = np.sum(matriz, axis=1, keepdims=True)

    # Reemplazar ceros en la suma para evitar divisiones por cero
    suma_filas[suma_filas == 0] = 1

    # Normalizar la matriz
    matriz_normalizada = matriz / suma_filas

    return matriz_normalizada

# Función para marginalizar y normalizar una matriz dado un conjunto de índices de filas y columnas
def marginalizar_y_normalizar(matriz, indices_filas, indices_columnas):
    """
    Realiza la marginalización y normalización de una matriz dado un conjunto de índices de filas y columnas.

    Parameters:
        matriz (np.ndarray): Matriz a procesar.
        indices_filas (list): Lista de índices de filas a marginalizar.
        indices_columnas (list): Lista de índices de columnas a marginalizar.

    Returns:
        np.ndarray: Matriz resultante después de la marginalización y normalización.
    """
    matriz_marginalizada = marginalizar(matriz, indices_columnas)
    matriz_normalizada = normalizar(matriz_marginalizada.reshape(-1, 2 ** len(indices_filas)))
    return matriz_normalizada.reshape(-1, 2 ** len(indices_filas))

# Función para generar muestras aleatorias
def generar_entradas_aleatorias(n, m):
    """
    Genera muestras aleatorias de longitud m.

    Parameters:
        n (int): Número de muestras a generar.
        m (int): Longitud de cada muestra.

    Returns:
        list: Lista de muestras generadas.
    """
    muestras = []
    for i in range(n):
        muestra = np.random.randint(2, size=m)
        muestras.append(muestra)
    return muestras

# Clase para la interfaz gráfica
class InterfazGrafica:
    def __init__(self):
        # Inicialización de la ventana y configuración de elementos
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
        self.btn_mostrar_resultados = ttk.Button(self.window, text="Mostrar Resultados", command=self.mostrar_resultados)
        self.btn_marginalizar_y_normalizar = ttk.Button(self.window, text="Marginalizar y Normalizar", command=self.marginalizar_y_normalizar)
        self.btn_marginalizar_y_normalizar.grid(row=15, column=0, columnspan=2, pady=5)
        self.btn_mostrar_datos = ttk.Button(self.window, text="Mostrar Datos ", command=self.mostrar_datos)
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
        self.btn_mostrar_resultados.grid(row=8, column=0, columnspan=2, pady=5)
        self.btn_mostrar_datos.grid(row=9, column=0, columnspan=2, pady=5)
        self.btn_cargar_csv.grid(row=10, column=0, columnspan=2, pady=5)
        self.btn_salir.grid(row=11, column=0, columnspan=2, pady=5)

    def ingresar_manualmente(self):
        """
        Permite al usuario ingresar manualmente el número de muestras y los valores de cada muestra.
        """
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
        """
        Genera datos aleatorios con el número de muestras y canales especificados.
        """
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
        """
        Muestra la matriz EstadoCanalF en una ventana de mensaje.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[0], "Matriz EstadoCanalF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_f(self):
        """
        Muestra la matriz EstadoEstadoF en una ventana de mensaje.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[1], "Matriz EstadoEstadoF")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_canal_p(self):
        """
        Muestra la matriz EstadoCanalP en una ventana de mensaje.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[2], "Matriz EstadoCanalP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_estado_p(self):
        """
        Muestra la matriz EstadoEstadoP en una ventana de mensaje.
        """
        if self.matrices is not None:
            self.mostrar_matriz(self.matrices[3], "Matriz EstadoEstadoP")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def marginalizar_y_normalizar(self):
        """
        Muestra la matriz EstadoFuturoBC y EstadoFuturoABC marginalizadas y normalizadas en una ventana de mensaje.
        """
        if self.matrices is not None:
            EstadoFuturo_BC = self.calcular_estado_futuro_BC()
            EstadoFuturo_ABC = self.calcular_estado_futuro_ABC()

            resultado_BC = marginalizar_y_normalizar(EstadoFuturo_BC, [0], [1])
            resultado_ABC = marginalizar_y_normalizar(EstadoFuturo_ABC, [0, 1], [2])

            self.mostrar_matriz(resultado_BC, "Estado Futuro BC (Marginalizado y Normalizado)")
            self.mostrar_matriz(resultado_ABC, "Estado Futuro ABC (Marginalizado y Normalizado)")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def mostrar_resultados(self):
        """
        Muestra la matriz EstadoFuturoBC y EstadoFuturoABC en una ventana de mensaje.
        """
        if self.matrices is not None:
            EstadoFuturo_BC = self.calcular_estado_futuro_BC()
            EstadoFuturo_ABC = self.calcular_estado_futuro_ABC()

            self.mostrar_matriz(EstadoFuturo_BC, "Estado Futuro BC")
            self.mostrar_matriz(EstadoFuturo_ABC, "Estado Futuro ABC")
        else:
            messagebox.showwarning("Advertencia", "Debe calcular las matrices primero (opción 1 o 2).")

    def calcular_estado_futuro_BC(self):
        """
        Calcula la matriz EstadoFuturoBC a partir de las matrices auxiliares.
        """
        EstadoFuturo_BC = np.zeros((2 ** 2, 2 ** 2), dtype=float)
        EstadoFuturo_ABC = np.zeros((2 ** 3, 2 ** 3), dtype=float)

        # Marginalización y normalización sobre el estado futuro ABC
        matriz_marginalizada = marginalizar_y_normalizar(self.matrices[1], [1, 2], [1, 2])

        # Asegúrate de que las dimensiones de matriz_marginalizada sean (2^2, 2^2)
        if matriz_marginalizada.shape == (2 ** 2, 2 ** 2):
            # Marginalización y normalización sobre el estado futuro BC
            EstadoFuturo_BC[:, 1:] = matriz_marginalizada

            # Asegúrate de que las dimensiones de EstadoFuturo_ABC[:, 2:] sean (2^2, 2^2)
            EstadoFuturo_ABC[:, 2:] = matriz_marginalizada
        else:
            messagebox.showerror("Error", "Dimensiones incorrectas para la matriz marginalizada")

        return EstadoFuturo_BC


    def calcular_estado_futuro_ABC(self):
        """
        Calcula la matriz EstadoFuturoABC a partir de las matrices auxiliares.
        """
        EstadoFuturo_ABC = np.zeros((2 ** 3, 2 ** 3), dtype=float)

        # Marginalización y normalización sobre el estado futuro ABC
        resultado_marginalizacion = marginalizar_y_normalizar(self.matrices[1], [1, 2], [1, 2])

        if resultado_marginalizacion.shape == (2 ** 3, 2 ** 2):
            EstadoFuturo_ABC[:, 2:] = resultado_marginalizacion
        else:
            messagebox.showerror("Error", "Dimensiones incorrectas para la matriz marginalizada")

        return EstadoFuturo_ABC

    def mostrar_datos(self):
        """
        Muestra las muestras generadas en una ventana de mensaje.
        """
        if self.muestras_almacenadas is not None:
            self.mostrar_matriz_datos(self.muestras_almacenadas)
        else:
            messagebox.showwarning("Advertencia", "No hay datos generados.")

    def cargar_csv(self):
        """
        Permite al usuario cargar un archivo CSV con las muestras.
        """
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
        """
        Muestra una matriz en una ventana de mensaje.
        """
        filas, columnas = matriz.shape
        df = pd.DataFrame(matriz, columns=[f'Estado {i}' for i in range(columnas)])

        # Utilizamos PrettyTable para mostrar la matriz de manera más legible
        pt = PrettyTable()
        pt.field_names = [f'Estado {i}' for i in range(columnas)]
        for _, row in df.iterrows():
            pt.add_row(row)

        # Mostramos la matriz en una ventana de mensaje
        messagebox.showinfo(titulo, f"{pt}")

    def mostrar_matriz_datos(self, muestras):
        """
        Muestra las muestras generadas en una ventana de mensaje.
        """
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
        """
        Muestra un dataframe en una ventana de mensaje.
        """
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
        """
        Ejecuta la interfaz gráfica.
        """
        self.window.mainloop()

if __name__ == "__main__":
    interfaz = InterfazGrafica()
    interfaz.run()