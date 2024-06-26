import random
import math
import networkx as nx
import matplotlib.pyplot as plt

# Generar posiciones de APs (x, y)
def generar_posiciones(num_aps, area):
    posiciones = []
    for _ in range(num_aps):
        x = random.uniform(0, area[0])
        y = random.uniform(0, area[1])
        posiciones.append((x, y))
    return posiciones

# Calcular adyacencias (vecindad) entre APs
def calcular_adyacencias(posiciones, rango_adyacencia):
    grafo = nx.Graph()
    num_aps = len(posiciones)
    for i in range(num_aps):
        for j in range(i + 1, num_aps):
            distancia = math.sqrt((posiciones[i][0] - posiciones[j][0])**2 + (posiciones[i][1] - posiciones[j][1])**2)
            if distancia < rango_adyacencia:
                grafo.add_edge(i, j)
    return grafo

# Asignar canales utilizando el algoritmo de coloreo de grafos
def asignar_canales(grafo):
    colores = nx.coloring.greedy_color(grafo, strategy="largest_first")
    return colores

# Visualizar APs y sus asignaciones de canales
def visualizar_aps(posiciones, colores):
    plt.figure()
    color_map = plt.colormaps.get_cmap('tab20', max(colores.values()) + 1)  # Mapa de colores con suficientes colores distintos
    for i, (x, y) in enumerate(posiciones):
        if i in colores:
            plt.scatter(x, y, color=color_map(colores[i] / max(colores.values())))
            plt.text(x, y, str(i), fontsize=12, ha='right')
    plt.show()

# Parámetros
num_aps = 10
area = (100, 100)
rango_adyacencia = 30

# Generar posiciones y calcular adyacencias
posiciones = generar_posiciones(num_aps, area)
grafo = calcular_adyacencias(posiciones, rango_adyacencia)

# Asignar canales
colores = asignar_canales(grafo)

# Visualizar resultado
visualizar_aps(posiciones, colores)

# Imprimir asignación de canales
for ap, canal in colores.items():
    print(f"AP {ap}: Canal {canal}")
