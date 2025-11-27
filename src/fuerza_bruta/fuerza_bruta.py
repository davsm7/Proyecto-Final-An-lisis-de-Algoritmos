import itertools

def tsp_fuerza_bruta(grafo, inicio=0):
    """
    grafo: matriz de adyacencia con los costos/distancias
    inicio: vértice inicial (por defecto 0)
    """
    n = len(grafo)
    vertices = list(range(n))
    vertices.remove(inicio)

    mejor_costo = float("inf")
    mejor_ruta = None

    # Probar todas las permutaciones posibles de los vértices
    for perm in itertools.permutations(vertices):
        costo = 0
        k = inicio
        # recorrer la ruta según la permutación
        for j in perm:
            costo += grafo[k][j]
            k = j
        # volver al inicio
        costo += grafo[k][inicio]

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_ruta = (inicio,) + perm + (inicio,)

    return mejor_costo, mejor_ruta


# ------------------------------
# Ejemplo de uso
# ------------------------------
if __name__ == "__main__":
    grafo = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    costo, ruta = tsp_fuerza_bruta(grafo)
    print("Costo mínimo encontrado:", costo)
    print("Ruta óptima:", ruta)