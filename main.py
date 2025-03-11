# Implementación de las librerías Networkx, TkInter, Random, Time y Threading.
# Autores: Vicente Vélez, Abel Salazar, Claudio Gutiérrez, Ricardo Gutiérrez, Guillermo Ibarra
import networkx as nx
import tkinter as tk
from tkinter import simpledialog, Toplevel, StringVar, Scrollbar, Label, Button, Entry, filedialog, messagebox
import random
import time
import threading
import json
import os


# Clase principal que representa el simulador de Packet Tracer.
# Esta clase gestiona la interfaz gráfica y la lógica de la simulación de redes.
class SimuladorPacketTracer:
    def __init__(self):
        # Grafo dirigido que representa la topología de la red.
        self.grafo = nx.DiGraph()
        # Lista de colores para diferenciar componentes fuertemente conectados.
        self.colores = ["red", "blue", "green", "purple", "orange"]

        # Configuración de la ventana principal de la aplicación.
        self.root = tk.Tk()
        self.root.title("Simulador Packet Tracer")
        self.root.geometry("1000x700")

        # Frame y Canvas para dibujar la topología de red.
        self.frame_canvas = tk.Frame(self.root)
        self.frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_canvas, bg="white")
        self.scroll_x = Scrollbar(self.frame_canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_y = Scrollbar(self.frame_canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.nodos_canvas = {}

        # Íconos simplificados: se usan colores en lugar de imágenes.
        self.iconos = {
            "PC": "#3498DB",
            "Router": "#E74C3C",
            "Switch": "#2ECC71",
            "Server": "#F39C12"
        }

        # Crear el menú de la aplicación y configurar eventos del mouse.
        self.crear_menu()
        self.canvas.bind("<B1-Motion>", self.mover_dispositivo)
        self.canvas.bind("<Button-3>", self.mostrar_menu_contextual)

    # Crea el menú de la aplicación con botones para realizar acciones como agregar dispositivos,
    # conexiones, ejecutar algoritmos, etc.
    def crear_menu(self):
        frame = tk.Frame(self.root, bg="#2C3E50", padx=10, pady=10)
        frame.pack(side=tk.RIGHT, fill=tk.Y)

        opciones = [
            ("Agregar Dispositivo", self.mostrar_menu_dispositivos),
            ("Agregar Conexión", self.agregar_conexion),
            ("Eliminar Dispositivo", self.eliminar_dispositivo),
            ("Eliminar Conexión", self.eliminar_conexion),
            ("Ejecutar Tarjan", self.ejecutar_tarjan),
            ("Simular Paquetes", self.simular_paquetes),
            ("Guardar Topología", self.guardar_topologia),
            ("Cargar Topología", self.cargar_topologia)
        ]

        for texto, comando in opciones:
            tk.Button(frame, text=texto, command=comando, font=("Arial", 12), bg="#34495E", fg="white", padx=10,
                      pady=5).pack(fill=tk.X, pady=5)

        self.info_label = tk.Label(frame, text="", fg="white", bg="#2C3E50", wraplength=180, justify=tk.LEFT)
        self.info_label.pack(pady=10)

    # Muestra un menú contextual al hacer clic derecho en el canvas.
    # Permite eliminar nodos o crear conexiones desde un nodo seleccionado.
    def mostrar_menu_contextual(self, event):
        x, y = event.x, event.y

        nodo_seleccionado = None
        for nodo, (shape, texto) in self.nodos_canvas.items():
            if self.dentro_nodo(x, y, shape):
                nodo_seleccionado = nodo
                break

        menu = tk.Menu(self.root, tearoff=0)

        if nodo_seleccionado:
            menu.add_command(label=f"Eliminar {nodo_seleccionado}",
                             command=lambda: self.eliminar_nodo_especifico(nodo_seleccionado))
            menu.add_command(label=f"Crear conexión desde {nodo_seleccionado}",
                             command=lambda: self.crear_conexion_desde(nodo_seleccionado))
        else:
            menu.add_command(label="Agregar dispositivo aquí",
                             command=lambda: self.agregar_dispositivo_en(x, y))

        menu.tk_popup(event.x_root, event.y_root)

    # Agrega un dispositivo en una posición específica del canvas.
    def agregar_dispositivo_en(self, x, y):
        menu = Toplevel(self.root)
        menu.title("Seleccionar Tipo de Dispositivo")
        menu.geometry("300x200")
        menu.configure(bg="#34495E")

        Label(menu, text="Seleccione el tipo de dispositivo:", fg="white", bg="#34495E",
              font=("Arial", 12)).pack(pady=10)
        tipo_var = StringVar()

        for tipo in ["PC", "Router", "Switch", "Server"]:
            tk.Radiobutton(menu, text=tipo, variable=tipo_var, value=tipo, bg="#34495E",
                           fg="white", selectcolor="#2C3E50").pack()

        def agregar():
            tipo = tipo_var.get()
            nombre = simpledialog.askstring("Agregar Dispositivo", "Ingrese el nombre del dispositivo:")
            if nombre:
                if nombre not in self.grafo:
                    self.grafo.add_node(nombre, pos=(x, y), tipo=tipo)
                    self.actualizar_visualizacion()
                else:
                    messagebox.showerror("Error", "Ya existe un dispositivo con ese nombre.")
            menu.destroy()

        Button(menu, text="Agregar", command=agregar, bg="#2ECC71", fg="white").pack(pady=10)

    # Crea una conexión desde un nodo específico hacia otro nodo.
    def crear_conexion_desde(self, origen):
        destino = simpledialog.askstring("Crear Conexión",
                                         f"Ingrese el nombre del dispositivo destino para conectar desde {origen}:")
        if destino and destino in self.grafo:
            if not self.grafo.has_edge(origen, destino):
                self.grafo.add_edge(origen, destino)
                self.actualizar_visualizacion()
            else:
                messagebox.showinfo("Información", "Esta conexión ya existe.")
        elif destino:
            messagebox.showerror("Error", "El dispositivo destino no existe.")

    # Elimina un nodo específico y todas sus conexiones.
    def eliminar_nodo_especifico(self, nodo):
        confirmacion = messagebox.askyesno("Confirmar",
                                           f"¿Está seguro de que desea eliminar el dispositivo '{nodo}' y todas sus conexiones?")
        if confirmacion:
            self.grafo.remove_node(nodo)
            self.actualizar_visualizacion()

    # Agrega una conexión entre dos dispositivos.
    def agregar_conexion(self):
        origen, destino = self.pedir_datos("Agregar Conexión", ["Origen", "Destino"])
        if origen in self.grafo and destino in self.grafo:
            if not self.grafo.has_edge(origen, destino):
                self.grafo.add_edge(origen, destino)
                self.actualizar_visualizacion()
            else:
                self.info_label.config(text="Esta conexión ya existe.")
        else:
            self.info_label.config(text="Error: Verifique que los dispositivos existen.")

    # Ejecuta el algoritmo de Tarjan para encontrar componentes fuertemente conectados.
    def ejecutar_tarjan(self):
        sccs = list(nx.strongly_connected_components(self.grafo))

        self.canvas.delete("componente")

        pos = nx.get_node_attributes(self.grafo, 'pos')

        for i, componente in enumerate(sccs):
            if len(componente) > 0:
                x_coords = [pos[nodo][0] for nodo in componente if nodo in pos]
                y_coords = [pos[nodo][1] for nodo in componente if nodo in pos]

                if x_coords and y_coords:
                    margen = 30
                    x_min = min(x_coords) - margen
                    y_min = min(y_coords) - margen
                    x_max = max(x_coords) + margen
                    y_max = max(y_coords) + margen

                    color = self.colores[i % len(self.colores)]

                    recuadro = self.canvas.create_rectangle(
                        x_min, y_min, x_max, y_max,
                        outline=color,
                        width=2,
                        fill=color,
                        stipple="gray25",
                        tags=("componente",)
                    )

                    self.canvas.tag_lower(recuadro)

                    self.canvas.create_text(
                        (x_min + x_max) / 2,
                        y_min - 10,
                        text=f"Componente {i + 1}",
                        fill=color,
                        font=("Arial", 10, "bold"),
                        tags=("componente",)
                    )

        if len(sccs) > 0:
            self.info_label.config(text=f"Se encontraron {len(sccs)} componentes fuertemente conectados.")
        else:
            self.info_label.config(text="No se encontraron componentes fuertemente conectados.")

    # Simula el envío de paquetes entre dos dispositivos.
    def simular_paquetes(self):
        origen, destino = self.pedir_datos("Simular Paquetes", ["Origen", "Destino"])
        if origen in self.grafo and destino in self.grafo:
            try:
                ruta = nx.shortest_path(self.grafo, source=origen, target=destino)
                threading.Thread(target=self.animar_paquete, args=(ruta,)).start()
            except nx.NetworkXNoPath:
                self.info_label.config(text="No hay ruta disponible entre los dispositivos.")

    # Anima el movimiento de un paquete a lo largo de una ruta.
    def animar_paquete(self, ruta):
        pos = nx.get_node_attributes(self.grafo, 'pos')
        paquete = self.canvas.create_oval(*self.obtener_coords(pos[ruta[0]], 5), fill="yellow")
        for i in range(len(ruta) - 1):
            x1, y1 = pos[ruta[i]]
            x2, y2 = pos[ruta[i + 1]]
            for _ in range(20):
                self.canvas.move(paquete, (x2 - x1) / 20, (y2 - y1) / 20)
                self.root.update()
                time.sleep(0.05)
        self.canvas.delete(paquete)

    # Muestra un menú para seleccionar el tipo de dispositivo a agregar.
    def mostrar_menu_dispositivos(self):
        menu = Toplevel(self.root)
        menu.title("Seleccionar Tipo de Dispositivo")
        menu.geometry("300x200")
        menu.configure(bg="#34495E")

        Label(menu, text="Seleccione el tipo de dispositivo:", fg="white", bg="#34495E",
              font=("Arial", 12)).pack(pady=10)
        tipo_var = StringVar()

        for tipo in ["PC", "Router", "Switch", "Server"]:
            tk.Radiobutton(menu, text=tipo, variable=tipo_var, value=tipo, bg="#34495E",
                           fg="white", selectcolor="#2C3E50").pack()

        Button(menu, text="Agregar", command=lambda: self.agregar_dispositivo(tipo_var.get(), menu),
               bg="#2ECC71", fg="white").pack(pady=10)

    # Agrega un dispositivo al grafo con un nombre y tipo específicos.
    def agregar_dispositivo(self, tipo, menu):
        menu.destroy()
        nombre = simpledialog.askstring("Agregar Dispositivo", "Ingrese el nombre del dispositivo:")
        if nombre:
            if nombre not in self.grafo:
                self.grafo.add_node(nombre, pos=(random.randint(50, 550), random.randint(50, 550)), tipo=tipo)
                self.actualizar_visualizacion()
            else:
                messagebox.showerror("Error", "Ya existe un dispositivo con ese nombre.")

    # Elimina un dispositivo del grafo.
    def eliminar_dispositivo(self):
        nombre = simpledialog.askstring("Eliminar Dispositivo", "Ingrese el nombre del dispositivo a eliminar:")
        if nombre and nombre in self.grafo:
            confirmacion = messagebox.askyesno("Confirmar",
                                               f"¿Está seguro de que desea eliminar el dispositivo '{nombre}' y todas sus conexiones?")
            if confirmacion:
                self.grafo.remove_node(nombre)
                self.actualizar_visualizacion()
        elif nombre:
            messagebox.showerror("Error", "El dispositivo no existe.")

    # Elimina una conexión entre dos dispositivos.
    def eliminar_conexion(self):
        origen, destino = self.pedir_datos("Eliminar Conexión", ["Origen", "Destino"])
        if origen in self.grafo and destino in self.grafo:
            if self.grafo.has_edge(origen, destino):
                confirmacion = messagebox.askyesno("Confirmar",
                                                   f"¿Está seguro de que desea eliminar la conexión de '{origen}' a '{destino}'?")
                if confirmacion:
                    self.grafo.remove_edge(origen, destino)
                    self.actualizar_visualizacion()
            else:
                self.info_label.config(text="La conexión no existe.")
        else:
            self.info_label.config(text="Error: Verifique que los dispositivos existen.")

    # Guarda la topología de red en un archivo JSON.
    def guardar_topologia(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            title="Guardar Topología"
        )

        if archivo:
            try:
                datos = {
                    "nodos": [],
                    "enlaces": []
                }

                for nodo, atributos in self.grafo.nodes(data=True):
                    datos_nodo = {"nombre": nodo}
                    datos_nodo.update(atributos)
                    if "pos" in datos_nodo:
                        datos_nodo["pos"] = list(datos_nodo["pos"])
                    datos["nodos"].append(datos_nodo)

                for origen, destino, atributos in self.grafo.edges(data=True):
                    datos_enlace = {"origen": origen, "destino": destino}
                    datos_enlace.update(atributos)
                    datos["enlaces"].append(datos_enlace)

                with open(archivo, "w") as f:
                    json.dump(datos, f, indent=4)

                self.info_label.config(text=f"Topología guardada en {os.path.basename(archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar la topología: {str(e)}")

    # Carga una topología de red desde un archivo JSON.
    def cargar_topologia(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            title="Cargar Topología"
        )

        if archivo:
            try:
                with open(archivo, "r") as f:
                    datos = json.load(f)

                nuevo_grafo = nx.DiGraph()

                for nodo_datos in datos["nodos"]:
                    nombre = nodo_datos.pop("nombre")
                    if "pos" in nodo_datos:
                        nodo_datos["pos"] = tuple(nodo_datos["pos"])
                    nuevo_grafo.add_node(nombre, **nodo_datos)

                for enlace_datos in datos["enlaces"]:
                    origen = enlace_datos.pop("origen")
                    destino = enlace_datos.pop("destino")
                    nuevo_grafo.add_edge(origen, destino, **enlace_datos)

                self.grafo = nuevo_grafo
                self.actualizar_visualizacion()

                self.info_label.config(text=f"Topología cargada desde {os.path.basename(archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la topología: {str(e)}")

    # Actualiza la visualización del grafo en el canvas.
    def actualizar_visualizacion(self):
        self.canvas.delete("all")
        pos = nx.get_node_attributes(self.grafo, 'pos')
        self.nodos_canvas.clear()

        for nodo, (x, y) in pos.items():
            tipo = self.grafo.nodes[nodo].get('tipo', "PC")
            color = self.iconos.get(tipo, "#3498DB")

            node_obj = self.canvas.create_oval(*self.obtener_coords((x, y), 15),
                                               fill=color, tags=nodo)

            texto_obj = self.canvas.create_text(x, y - 25, text=nodo, font=("Arial", 10))
            self.nodos_canvas[nodo] = (node_obj, texto_obj)

        for origen, destino in self.grafo.edges():
            if origen in pos and destino in pos:
                x1, y1 = pos[origen]
                x2, y2 = pos[destino]
                self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, tags="linea")

    # Actualiza las conexiones en el canvas.
    def actualizar_conexiones(self):
        self.canvas.delete("linea")

        pos = nx.get_node_attributes(self.grafo, 'pos')
        for origen, destino in self.grafo.edges():
            if origen in pos and destino in pos:
                x1, y1 = pos[origen]
                x2, y2 = pos[destino]
                self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, tags="linea")

    # Mueve un dispositivo en el canvas.
    def mover_dispositivo(self, event):
        for nodo, (shape, texto) in self.nodos_canvas.items():
            if self.dentro_nodo(event.x, event.y, shape):
                dx, dy = event.x - self.canvas.coords(shape)[0] - 15, event.y - self.canvas.coords(shape)[1] - 15
                self.canvas.move(shape, dx, dy)
                self.canvas.move(texto, dx, dy)
                self.grafo.nodes[nodo]['pos'] = (event.x, event.y)

                self.actualizar_conexiones()
                break

    # Obtiene las coordenadas de un nodo.
    def obtener_coords(self, pos, r):
        return pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r

    # Verifica si un punto está dentro de un nodo.
    def dentro_nodo(self, x, y, shape):
        coords = self.canvas.coords(shape)
        if len(coords) == 4:
            return coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]
        return False

    # Pide datos al usuario mediante una ventana emergente.
    def pedir_datos(self, titulo, campos):
        ventana = Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("300x200")
        ventana.configure(bg="#34495E")

        valores = []
        entradas = []

        Label(ventana, text=titulo, fg="white", bg="#34495E", font=("Arial", 12, "bold")).pack(pady=10)

        for campo in campos:
            Label(ventana, text=campo + ":", fg="white", bg="#34495E").pack()
            entrada = Entry(ventana)
            entrada.pack()
            entradas.append(entrada)

        def obtener_valores():
            for entrada in entradas:
                valores.append(entrada.get())
            ventana.destroy()

        Button(ventana, text="Aceptar", command=obtener_valores, bg="#2ECC71", fg="white").pack(pady=10)
        ventana.wait_window()

        return valores

    # Ejecuta la aplicación.
    def ejecutar(self):
        self.root.mainloop()


if __name__ == "__main__":
    SimuladorPacketTracer().ejecutar()