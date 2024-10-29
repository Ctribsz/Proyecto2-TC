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

def extraer_no_terminales(producciones):
    """
    Extrae los no terminales de las producciones en la gramática.

    :param producciones: Diccionario de reglas de producción {no_terminal: [[producción_1], [producción_2], ...]}.
    :return: Lista de no terminales en la gramática.
    """
    no_terminales = set(producciones.keys())

    for rhs_list in producciones.values():
        for produccion in rhs_list:
            for simbolo in produccion:
                # Verifica si el símbolo es un no terminal (si es mayúscula y está en las claves del diccionario)
                if simbolo.isupper() and simbolo in producciones:
                    no_terminales.add(simbolo)

    return list(no_terminales)

def extraer_terminales(producciones, no_terminales):
    """
    Extrae los terminales de las producciones en la gramática.

    :param producciones: Diccionario de reglas de producción {no_terminal: [[producción_1], [producción_2], ...]}.
    :param no_terminales: Lista de no terminales en la gramática.
    :return: Lista de terminales en la gramática.
    """
    terminales = set()

    for rhs_list in producciones.values():
        for produccion in rhs_list:
            for simbolo in produccion:
                # Si el símbolo no está en los no terminales y no es vacío, es un terminal
                if simbolo not in no_terminales and simbolo != 'ε':
                    terminales.add(simbolo)

    return list(terminales)
