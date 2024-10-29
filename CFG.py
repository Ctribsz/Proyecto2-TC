# Proyecto 2 - Christian Echeverría
# Teoria de la computación

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
    Elimina la recursividad a la izquierda en la gramática.
    :param gramatica: Diccionario que representa las producciones de la gramática.
    :return: Gramática sin recursividad a la izquierda.
    """
    nueva_gramatica = {}

    for no_terminal, producciones in gramatica.items():
        recursivas = []
        no_recursivas = []

        for produccion in producciones:
            if produccion[0] == no_terminal:
                recursivas.append(produccion[1:])  # Separar el símbolo recursivo
            else:
                no_recursivas.append(produccion)

        if recursivas:
            # Crear un nuevo símbolo para eliminar la recursividad
            nuevo_no_terminal = no_terminal + "'"
            nueva_gramatica[no_terminal] = []
            nueva_gramatica[nuevo_no_terminal] = []

            # Agregar las producciones modificadas
            for prod in no_recursivas:
                nueva_gramatica[no_terminal].append(prod + [nuevo_no_terminal])
            for prod in recursivas:
                nueva_gramatica[nuevo_no_terminal].append(prod + [nuevo_no_terminal])
            nueva_gramatica[nuevo_no_terminal].append(['ε'])  # Producción epsilon
        else:
            nueva_gramatica[no_terminal] = producciones

    return nueva_gramatica

def eliminar_epsilon(gramatica):
    """
    Elimina las producciones epsilon de la gramática.
    :param gramatica: Diccionario que representa las producciones de la gramática.
    :return: Gramática sin producciones epsilon.
    """
    # Identificar no terminales que producen epsilon
    generadores_epsilon = set()
    for no_terminal, producciones in gramatica.items():
        for produccion in producciones:
            if produccion == ['ε']:
                generadores_epsilon.add(no_terminal)

    # Remover producciones epsilon directas
    for no_terminal in generadores_epsilon:
        gramatica[no_terminal] = [prod for prod in gramatica[no_terminal] if prod != ['ε']]

    # Expandir la gramática para incluir combinaciones sin los generadores de epsilon
    for no_terminal, producciones in list(gramatica.items()):
        nuevas_producciones = set()  # Usar un conjunto para evitar duplicados
        for produccion in producciones:
            # Generar combinaciones al omitir símbolos que generan epsilon
            combinaciones = [produccion]
            for simbolo in produccion:
                if simbolo in generadores_epsilon:
                    nuevas_combinaciones = []
                    for comb in combinaciones:
                        # Agregar la combinación sin el símbolo
                        nueva_comb = [s for s in comb if s != simbolo]
                        nuevas_combinaciones.append(comb)  # Con símbolo
                        if nueva_comb:  # Solo añadir si no está vacío
                            nuevas_combinaciones.append(nueva_comb)  # Sin símbolo
                    combinaciones = nuevas_combinaciones
            # Añadir combinaciones únicas
            nuevas_producciones.update(tuple(comb) for comb in combinaciones if comb)

        gramatica[no_terminal].extend(list(nuevas_producciones))

    # Convertir las producciones nuevamente a listas
    for no_terminal, producciones in gramatica.items():
        gramatica[no_terminal] = [list(prod) for prod in set(tuple(p) for p in producciones)]

    return gramatica

def eliminar_unarias(gramatica):
    """
    Elimina las producciones unitarias de la gramática.
    :param gramatica: Diccionario que representa las producciones de la gramática.
    :return: Gramática sin producciones unitarias.
    """
    # Crear un diccionario para almacenar las producciones sin las unitarias
    nueva_gramatica = {nt: [] for nt in gramatica}

    # Para cada no terminal, eliminar producciones unitarias
    for no_terminal, producciones in gramatica.items():
        # Encontrar todas las producciones no unitarias directamente
        no_unitarias = [prod for prod in producciones if len(prod) != 1 or prod[0] not in gramatica]
        nueva_gramatica[no_terminal].extend(no_unitarias)

        # Encontrar producciones unitarias y sus derivaciones finales
        unitarias = [prod[0] for prod in producciones if len(prod) == 1 and prod[0] in gramatica]
        while unitarias:
            unidad = unitarias.pop()
            for prod in gramatica[unidad]:
                # Si es una producción no unitaria, añadirla
                if len(prod) != 1 or prod[0] not in gramatica:
                    if prod not in nueva_gramatica[no_terminal]:
                        nueva_gramatica[no_terminal].append(prod)
                # Si es otra producción unitaria, añadir para verificar
                elif prod[0] not in unitarias:
                    unitarias.append(prod[0])

    return nueva_gramatica

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

            for produccion in gramatica_generativa[simbolo]:
                for simbolo_produccion in produccion:
                    if simbolo_produccion.isupper() and simbolo_produccion not in alcanzables:
                        por_explorar.append(simbolo_produccion)

    gramatica_final = {nt: prods for nt, prods in gramatica_generativa.items() if nt in alcanzables}

    return gramatica_final

def procesar_terminales(terminales, gramatica, no_terminales):
    """
    Convierte los terminales en no terminales solo en producciones largas (de más de un símbolo).
    Mantiene terminales en producciones unitarias intactas (como `PP -> with`).

    :param terminales: Conjunto de terminales de la gramática.
    :param gramatica: Diccionario de reglas de la gramática en CNF.
    :param no_terminales: Conjunto de no terminales de la gramática.
    :return: Nueva gramática donde los terminales en producciones largas son reemplazados.
    """
    nuevas_producciones = {}
    nuevos_no_terminales = {}

    # Genera un nuevo símbolo no terminal para cada terminal si es necesario
    for terminal in terminales:
        nuevo_no_terminal = f"q{len(nuevos_no_terminales) + 1}"
        nuevos_no_terminales[terminal] = nuevo_no_terminal
        nuevas_producciones[nuevo_no_terminal] = [[terminal]]  # Producción unitaria para el terminal

    # Procesa cada producción en la gramática
    for no_terminal, producciones in gramatica.items():
        nuevas_producciones[no_terminal] = []

        for rhs in producciones:
            # Solo reemplazar terminales en producciones largas (de más de un símbolo)
            if len(rhs) > 1:
                nueva_produccion = []
                for simbolo in rhs:
                    # Si es un terminal en una producción larga, reemplazar por su no terminal asignado
                    if simbolo in terminales:
                        nuevo_no_terminal = nuevos_no_terminales[simbolo]
                        nueva_produccion.append(nuevo_no_terminal)
                    else:
                        nueva_produccion.append(simbolo)
                nuevas_producciones[no_terminal].append(nueva_produccion)
            else:
                # Mantener producciones unitarias con terminales intactas
                nuevas_producciones[no_terminal].append(rhs)

    return nuevas_producciones

def convertir_a_cnf(gramatica):
    """
    Convierte las producciones largas en producciones binarias para cumplir con CNF.
    :param gramatica: Diccionario con las producciones de la gramática.
    :return: Gramática convertida a CNF.
    """
    contador_no_terminales = 1
    gramatica_cnf = {}

    for no_terminal, producciones in gramatica.items():
        gramatica_cnf[no_terminal] = []

        for produccion in producciones:
            # Dividir producciones largas en binarias
            while len(produccion) > 2:
                A, B = produccion[0], produccion[1]
                nuevo_no_terminal = f"C{contador_no_terminales}"
                contador_no_terminales += 1
                gramatica_cnf[nuevo_no_terminal] = [[A, B]]
                produccion = [nuevo_no_terminal] + produccion[2:]

            gramatica_cnf[no_terminal].append(produccion)

    return gramatica_cnf
