from graphviz import Digraph

def cyk_algorithm(w, reglas, simbolo_inicial):
    n = len(w)
    T = [[set() for _ in range(n)] for _ in range(n)]
    derivaciones = [[{} for _ in range(n)] for _ in range(n)]  # Guardar derivaciones

    # Inicializar con terminales
    for j in range(n):
        for lhs, rhs_list in reglas.items():
            for rhs in rhs_list:
                if len(rhs) == 1 and rhs[0] == w[j]:  # Comparar terminales directamente
                    T[j][j].add(lhs)
                    derivaciones[j][j][lhs] = w[j]  # Guardar derivación

    # Llenado de la tabla para subsecuencias
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                for lhs, rhs_list in reglas.items():
                    for rhs in rhs_list:
                        if len(rhs) == 2:
                            B, C = rhs
                            if B in T[i][k] and C in T[k + 1][j]:
                                T[i][j].add(lhs)
                                derivaciones[i][j][lhs] = (B, C, i, k, j)  # Guardar derivación con posiciones

    # Verificar pertenencia y construir el árbol si es válido
    if simbolo_inicial in T[0][n - 1]:
        print("La cadena pertenece al lenguaje.")
        construir_arbol(derivaciones, simbolo_inicial, 0, n - 1)
    else:
        print("La cadena NO pertenece al lenguaje.")

    return derivaciones

def construir_arbol(derivaciones, simbolo_inicial, i, j):
    dot = Digraph(comment="Árbol de derivación CYK")

    def agregar_nodos(derivaciones, simbolo, i, j, dot):
        nodo_id = f"{simbolo}_{i}_{j}"
        dot.node(nodo_id, simbolo)

        deriv = derivaciones[i][j].get(simbolo)
        if isinstance(deriv, tuple):
            B, C, i, k, j = deriv
            agregar_nodos(derivaciones, B, i, k, dot)
            agregar_nodos(derivaciones, C, k + 1, j, dot)
            dot.edge(nodo_id, f"{B}_{i}_{k}")
            dot.edge(nodo_id, f"{C}_{k + 1}_{j}")
        elif isinstance(deriv, str):  # Terminal
            dot.node(f"{deriv}_{i}_{j}", deriv)
            dot.edge(nodo_id, f"{deriv}_{i}_{j}")

    agregar_nodos(derivaciones, simbolo_inicial, i, j, dot)
    dot.render("arbol_derivacion_cyk", format="png", view=True)
