# Proyecto 2 - Christian Echeverría
# Teoria de la computación

def print_g (gramatica):
    for no_terminal, producciones in gramatica.items():
        producciones_formateadas = " | ".join(" ".join(prod) for prod in producciones)
        print(f"{no_terminal} -> {producciones_formateadas}")

def gr_reader(file_path):
    gramatica = {}
    simbolo_inicial = None

    with open(file_path, 'r') as file:
        for linea in file:
            linea = linea.strip()

            # Aquí nos encargamos de separar la parte izquierda de la derecha
            # La parte de la producción y del símbolo que la produce
            if "->" in linea:
                no_terminal, producciones = linea.split("->")
                no_terminal = no_terminal.strip()
                producciones = producciones.strip().split("|")

                # Si es la primera vez que vemos un no terminal, lo usamos como símbolo inicial
                if simbolo_inicial is None:
                    simbolo_inicial = no_terminal

                if no_terminal not in gramatica:
                    gramatica[no_terminal] = [prod.strip().split() for prod in producciones]
                else:
                    gramatica[no_terminal].extend([prod.strip().split() for prod in producciones])

    print("\nGramática leída:")
    for nt, prods in gramatica.items():
        for prod in prods:
            print(f"{nt} -> {' '.join(prod)}")

    return gramatica, simbolo_inicial

def descomponer_producciones(gramatica):
    """
    Descompone las producciones con múltiples símbolos en el lado derecho para cumplir con la CNF.
    :param gramatica: Diccionario que representa la gramática.
    :return: Gramática con producciones binarias.
    """
    nueva_gramatica = {}
    contador_auxiliar = 1

    for no_terminal, producciones in gramatica.items():
        nueva_gramatica[no_terminal] = []

        for produccion in producciones:
            while len(produccion) > 2:
                nuevo_no_terminal = f"X{contador_auxiliar}"
                contador_auxiliar += 1

                nueva_gramatica[nuevo_no_terminal] = [[produccion[0], produccion[1]]]
                produccion = [nuevo_no_terminal] + produccion[2:]

            nueva_gramatica[no_terminal].append(produccion)

    return nueva_gramatica

def eliminar_recursividad_izquierda(gramatica):
    """
    Elimina la recursividad a la izquierda (directa e indirecta) de una gramática.
    :param gramatica: Diccionario que representa la gramática.
    :return: Nueva gramática sin recursividad a la izquierda.
    """
    no_terminales = list(gramatica.keys())
    nueva_gramatica = {}

    for i, no_terminal in enumerate(no_terminales):
        nuevas_producciones = []

        print(f"\nProcesando {no_terminal}: {gramatica[no_terminal]}")

        for produccion in gramatica[no_terminal]:
            if produccion[0] in no_terminales[:i]:
                print(f"Encontrada recursividad indirecta: {no_terminal} -> {produccion}")
                for prod in gramatica[produccion[0]]:
                    nuevas_producciones.append(prod + produccion[1:])
                    print(f"Sustituida producción: {produccion} por {prod + produccion[1:]}")
            else:
                nuevas_producciones.append(produccion)

        print(f"Producciones reescritas para {no_terminal}: {nuevas_producciones}")

        recursivas = []
        no_recursivas = []
        for produccion in nuevas_producciones:
            if produccion[0] == no_terminal:
                print(f"Recursiva encontrada: {no_terminal} -> {produccion}")
                recursivas.append(produccion[1:])  # Guardamos α
            else:
                no_recursivas.append(produccion)

        if recursivas:
            nuevo_no_terminal = no_terminal + "'"

            nueva_gramatica[no_terminal] = [[*prod, nuevo_no_terminal] for prod in no_recursivas]
            print(f"Nuevas producciones para {no_terminal}: {nueva_gramatica[no_terminal]}")

            nueva_gramatica[nuevo_no_terminal] = [[*alpha, nuevo_no_terminal] for alpha in recursivas]
            nueva_gramatica[nuevo_no_terminal].append(['ε'])  # Agregar epsilon para terminar recursividad
            print(f"Producciones recursivas para {nuevo_no_terminal}: {nueva_gramatica[nuevo_no_terminal]}")
        else:
            nueva_gramatica[no_terminal] = no_recursivas
            print(f"Sin recursividad para {no_terminal}, nuevas producciones: {nueva_gramatica[no_terminal]}")

    return nueva_gramatica

def eliminar_e(gramatica):
    producciones_e = set()

    # Primero encontramos las producciones de tipo epsilon directas
    for non_terminal, producciones in gramatica.items():
        for produccion in producciones:
            if produccion == ['ε']:
                producciones_e.add(non_terminal)

    # Se itera sobre las producciones para hacer un match de cuales pueden ser
    # indirectamente anulables y si se encuentra se vuelve a hacer esto para que la
    # nueva produccion tambien se "tome en cuenta" a la hora de quitar anulables
    prod_anulables = True
    while prod_anulables:
        prod_anulables = False
        for non_terminal, producciones in gramatica.items():
            for produccion in producciones:
                if all(symbol in producciones_e for symbol in produccion):
                   if non_terminal not in producciones_e:
                      producciones_e.add(non_terminal)
                      prod_anulables = True

    return producciones_e

def crear_producciones_sinE(produccion, producciones_e):
    """
    Genera combinaciones de producciones después de eliminar producciones epsilon.
    """
    resultantes = set()
    cantidad_anulables = sum(1 for symbol in produccion if symbol in producciones_e)

    # Generar todas las combinaciones posibles de mantener o eliminar los anulables
    for i in range(2**cantidad_anulables):
        nueva_produccion = []
        nulable_count = 0
        for symbol in produccion:
            if symbol in producciones_e:
                # Decidir si eliminamos este símbolo nulable en esta combinación
                if i & (1 << nulable_count):
                    nueva_produccion.append(symbol)
                nulable_count += 1
            else:
                nueva_produccion.append(symbol)

        # Evitar producciones vacías y agregar la producción válida
        if nueva_produccion and nueva_produccion != ['e']:
            resultantes.add(tuple(nueva_produccion))

    return [list(prod) for prod in resultantes]

def eliminar_producciones_e(gramatica):
    producciones_e = eliminar_e(gramatica)

    nueva_gramatica_sinE = {}
    for no_terminal, producciones in gramatica.items():
        nuevas_producciones = set()
        for produccion in producciones:
            if produccion == ['ε']:
                continue
            else:
                combinaciones = crear_producciones_sinE(produccion, producciones_e)
                nuevas_producciones.update(tuple(p) for p in combinaciones if p != ['e'])


        nueva_gramatica_sinE[no_terminal] = [list(prod) for prod in nuevas_producciones]

    return nueva_gramatica_sinE

def eliminar_unarias(nueva_gramatica):
    nueva_grama_sinU = {}

    for no_terminal in nueva_gramatica:
        nueva_grama_sinU[no_terminal] = [prod for prod in nueva_gramatica[no_terminal] if len(prod) > 1 or not prod[0].isupper()]

    for no_terminal, producciones in nueva_gramatica.items():
        unitarias = [prod[0] for prod in producciones if len(prod) == 1 and prod[0].isupper()]
        while unitarias:
            U = unitarias.pop()
            if U in nueva_gramatica:
                for prod_de_U in nueva_gramatica[U]:
                    if len(prod_de_U) > 1 or not prod_de_U[0].isupper():
                        if prod_de_U not in nueva_grama_sinU[no_terminal]:
                            nueva_grama_sinU[no_terminal].append(prod_de_U)

    return nueva_grama_sinU

def eliminar_inutiles(gramatica, simbolo_inicial):
    """
    Elimina las producciones inútiles de la gramática, tanto las no alcanzables como las no generativas.
    :param gramatica: Diccionario que representa la gramática.
    :param simbolo_inicial: El símbolo inicial de la gramática.
    :return: Nueva gramática sin producciones inútiles.
    """
    generativas = set()
    for no_terminal, producciones in gramatica.items():
        for produccion in producciones:
            if all(not symbol.isupper() for symbol in produccion):  # Si todas son terminales
                generativas.add(no_terminal)

    cambio = True
    while cambio:
        cambio = False
        for no_terminal, producciones in gramatica.items():
            if no_terminal not in generativas:
                for produccion in producciones:
                    if all(symbol in generativas or not symbol.isupper() for symbol in produccion):
                        generativas.add(no_terminal)
                        cambio = True

    gramatica_generativa = {nt: [prod for prod in prods if all(symbol in generativas or not symbol.isupper() for symbol in prod)]
                            for nt, prods in gramatica.items() if nt in generativas}

    alcanzables = set()
    por_explorar = [simbolo_inicial]

    print(f"Símbolo inicial: {simbolo_inicial}")

    while por_explorar:
        simbolo = por_explorar.pop()
        if simbolo in gramatica_generativa and simbolo not in alcanzables:
            alcanzables.add(simbolo)
            print(f"Alcanzable: {simbolo}")

            for produccion in gramatica_generativa[simbolo]:
                for simbolo_produccion in produccion:
                    if simbolo_produccion.isupper() and simbolo_produccion not in alcanzables:
                        print(f"Explorando: {simbolo_produccion} desde {simbolo}")
                        por_explorar.append(simbolo_produccion)

    gramatica_final = {nt: prods for nt, prods in gramatica_generativa.items() if nt in alcanzables}

    print(f"Producciones alcanzables después de este paso: {gramatica_final}")

    return gramatica_final

def procesar_terminales(gramatica):
    """
    Convierte los terminales en producciones separadas de CNF.
    :param gramatica: Diccionario con las producciones.
    :return: Nueva gramática con los terminales convertidos.
    """
    nuevos_no_terminales = {}
    gramatica_cnf = {}

    def obtener_no_terminal_para_terminal(terminal):
        if terminal == "Det":
            return ["a", "the"]
        if terminal not in nuevos_no_terminales:
            nuevo_no_terminal = f"T_{terminal.upper()}"
            nuevos_no_terminales[terminal] = nuevo_no_terminal
            gramatica_cnf[nuevo_no_terminal] = [[terminal]]
        return [nuevos_no_terminales[terminal]]

    contador_no_terminales = 1

    for no_terminal, producciones in gramatica.items():
        gramatica_cnf[no_terminal] = []

        for produccion in producciones:
            nueva_produccion = []
            for simbolo in produccion:
                if not simbolo.isupper():
                    nueva_produccion += obtener_no_terminal_para_terminal(simbolo)
                else:
                    nueva_produccion.append(simbolo)

            while len(nueva_produccion) > 2:
                A, B = nueva_produccion[0], nueva_produccion[1]
                nuevo_no_terminal = f"T_{contador_no_terminales}"
                contador_no_terminales += 1
                gramatica_cnf[nuevo_no_terminal] = [[A, B]]
                nueva_produccion = [nuevo_no_terminal] + nueva_produccion[2:]

            gramatica_cnf[no_terminal].append(nueva_produccion)

    return gramatica_cnf


def convertir_a_CNF(gramatica):
    """
    Convierte una gramática a Forma Normal de Chomsky (CNF) después de que los terminales han sido manejados.
    """
    gramatica_cnf = {}
    contador_no_terminales = 1

    for no_terminal, producciones in gramatica.items():
        gramatica_cnf[no_terminal] = []
        for produccion in producciones:
            if len(produccion) == 2:
                gramatica_cnf[no_terminal].append(produccion)
            else:
                nueva_produccion = produccion
                while len(nueva_produccion) > 2:
                    A, B = nueva_produccion[0], nueva_produccion[1]
                    nuevo_no_terminal = f"X_{contador_no_terminales}"
                    contador_no_terminales += 1
                    gramatica_cnf[nuevo_no_terminal] = [[A, B]]
                    nueva_produccion = [nuevo_no_terminal] + nueva_produccion[2:]

                gramatica_cnf[no_terminal].append(nueva_produccion)

    return gramatica_cnf

def extraer_gramatica_cnf(cnf_gramatica):
    """
    Extrae los no terminales, terminales y las reglas de producción
    de la gramática en CNF.
    :param cnf_gramatica: Gramática en forma de diccionario.
    :return: no_terminales, terminales, reglas de producción
    """
    no_terminales = set()
    terminales = set()
    reglas = {}

    for lhs, rhs_list in cnf_gramatica.items():
        no_terminales.add(lhs)
        for rhs in rhs_list:
            if len(rhs) == 1 and rhs[0].islower():
                terminales.add(rhs[0])
            if lhs not in reglas:
                reglas[lhs] = []
            reglas[lhs].append(rhs)

    return list(no_terminales), list(terminales), reglas

def cyk_parse(w, reglas, no_terminales, terminales):
    n = len(w)

    T = [[set() for j in range(n)] for i in range(n)]

    for j in range(n):
        for lhs, rhs_list in reglas.items():
            for rhs in rhs_list:
                if len(rhs) == 1 and rhs[0] == w[j]:
                    T[j][j].add(lhs)
                    print(f"Palabra '{w[j]}' generada por '{lhs}' en la posición [{j},{j}]")


    for l in range(2, n+1):
        for i in range(n-l+1):
            j = i + l - 1
            for k in range(i, j):
                for lhs, rhs_list in reglas.items():
                    for rhs in rhs_list:
                        if len(rhs) == 2:
                            if rhs[0] in T[i][k] and rhs[1] in T[k+1][j]:
                                T[i][j].add(lhs)
                                print(f"Combinación exitosa: {rhs[0]} y {rhs[1]} generan {lhs} en la posición [{i},{j}]")
                            else:
                                if rhs[0] not in T[i][k]:
                                    print(f"No se encontró {rhs[0]} en la posición [{i},{k}]")
                                if rhs[1] not in T[k+1][j]:
                                    print(f"No se encontró {rhs[1]} en la posición [{k+1},{j}]")

    if 'S' in T[0][n-1]:
        print("La cadena pertenece al lenguaje.")
    else:
        print("La cadena NO pertenece al lenguaje.")

    print("\nTabla CYK completa:")
    for row in T:
        print(row)

file_path = "gramaticas.txt"

gramatica, simbolo_inicial = gr_reader(file_path)

print("\nGramática original leída desde el archivo:")
print_g(gramatica)
print(f"\nSímbolo inicial: {simbolo_inicial}")

gramatica_sinR = eliminar_recursividad_izquierda(gramatica)

gramatica_sinE = eliminar_producciones_e(gramatica_sinR)
print("\nProducciones después de eliminar epsilon:")
print_g(gramatica_sinE)

gramatica_sinU = eliminar_unarias(gramatica_sinE)
print("\nProducciones después de eliminar unitarias:")
print_g(gramatica_sinU)

gramatica_sin_inutiles = eliminar_inutiles(gramatica_sinU, simbolo_inicial)
print("\nProducciones después de eliminar inútiles:")
print_g(gramatica_sin_inutiles)

gramatica_procesada_terminales = procesar_terminales(gramatica_sin_inutiles)
print("\nProducciones después de procesar terminales:")
print_g(gramatica_procesada_terminales)

gramatica_CNF = convertir_a_CNF(gramatica_procesada_terminales)
print("\nGramática en CNF:")
print_g(gramatica_CNF)


no_terminales, terminales, reglas = extraer_gramatica_cnf(gramatica_CNF)

print("No terminales:", no_terminales)
print("Terminales:", terminales)
print("Reglas de producción:", reglas)

cyk_parse(['she', 'cooks'], reglas, no_terminales, terminales)
