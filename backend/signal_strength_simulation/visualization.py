import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles):
    plt.figure(figsize=(10, 8))
    contour = plt.contourf(X, Y, rx_power_total_dbm, cmap='coolwarm')
    plt.colorbar(contour, label='Potencia recibida total (dBm)')
    for i, pos in enumerate(device_positions):
        plt.plot(pos[0], pos[1], 'ro', markersize=10, label=f'Dispositivo Wi-Fi {i+1}')
    for obstacle in obstacles:
        vertices = obstacle['vertices']
        poly = patches.Polygon(vertices, fill=False, color='gray', alpha=0.7)
        plt.gca().add_patch(poly)
    plt.xlabel('Distancia (m)')
    plt.ylabel('Distancia (m)')
    plt.title('Mapa de contorno de la señal de RF con obstáculos')
    plt.legend()
    plt.tight_layout()
    plt.show()

def visualize_rays(rays, obstacles):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Dibujar los obstáculos
    for obstacle in obstacles:
        vertices = obstacle['vertices']
        vertices.append(vertices[0])  # Cerrar el polígono
        xs, ys = zip(*vertices)
        ax.plot(xs, ys, 'k-')

    # Dibujar los rayos
    for ray in rays:
        xs = [ray.start_pos[0], ray.end_pos[0]]
        ys = [ray.start_pos[1], ray.end_pos[1]]
        ax.plot(xs, ys, 'b-', linewidth=1)

    # Configurar los límites de los ejes
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_aspect('equal')

    plt.show()