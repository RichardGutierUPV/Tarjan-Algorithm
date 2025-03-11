# Tarjan-Algorithm
Simulador de Packet Tracer con Algoritmo de Tarjan
Este proyecto es un simulador de redes básico que utiliza el algoritmo de Tarjan para identificar componentes fuertemente conectados en una topología de red. Aunque el simulador se inspiró en herramientas como Packet Tracer, su objetivo principal es demostrar la aplicación práctica del algoritmo de Tarjan en redes.

Características principales
Algoritmo de Tarjan: Identifica componentes fuertemente conectados en la red.

Creación de dispositivos: Agrega dispositivos como PCs, Routers, Switches y Servidores.

Conexiones entre dispositivos: Establece conexiones entre dispositivos para simular una red.

Simulación de paquetes: Visualiza el envío de paquetes entre dispositivos utilizando el camino más corto.

Guardar y cargar topologías: Guarda y carga topologías de red en formato JSON.

Interfaz gráfica intuitiva: Utiliza tkinter para una interfaz fácil de usar.

Requisitos
Python 3.x: Asegúrate de tener Python instalado.

Librerías necesarias:

networkx: Para manejar grafos y operaciones de red.

tkinter: Para la interfaz gráfica.

Instala las dependencias con:

bash
Copy
pip install networkx
Cómo usar el simulador
Ejecutar el programa:

Clona el repositorio o descarga el código.

Ejecuta el archivo principal:

bash
Copy
python simulador_packet_tracer.py
Interfaz gráfica:

Agregar dispositivos: Haz clic derecho en el canvas para agregar un dispositivo en una posición específica.

Crear conexiones: Usa el botón "Agregar Conexión" para conectar dos dispositivos.

Simular paquetes: Usa el botón "Simular Paquetes" para enviar paquetes entre dispositivos.

Ejecutar Tarjan: Usa el botón "Ejecutar Tarjan" para identificar componentes fuertemente conectados.

Guardar y cargar topologías: Usa los botones "Guardar Topología" y "Cargar Topología" para guardar o cargar una red.

Movimiento de dispositivos:

Arrastra los dispositivos con el mouse para moverlos en el canvas.

Ejemplo de uso
Agregar dispositivos:

Haz clic derecho en el canvas y selecciona "Agregar dispositivo aquí".

Elige el tipo de dispositivo (PC, Router, Switch, Server) y asigna un nombre.

Crear conexiones:

Usa el botón "Agregar Conexión" para conectar dos dispositivos.

Simular paquetes:

Usa el botón "Simular Paquetes" para enviar paquetes entre dispositivos. El simulador mostrará la ruta más corta.

Ejecutar Tarjan:

Usa el botón "Ejecutar Tarjan" para identificar componentes fuertemente conectados en la red.

Guardar y cargar:

Guarda tu topología con "Guardar Topología" y cárgala más tarde con "Cargar Topología".

Limitaciones
Interfaz gráfica básica: La interfaz es funcional pero no está optimizada para grandes redes.

Escalabilidad: El simulador está diseñado para redes pequeñas o medianas. Puede volverse lento con redes muy grandes.

¡Gracias por usar este simulador! Esperamos que sea útil para aprender y experimentar con el algoritmo de Tarjan y conceptos de redes. 😊
