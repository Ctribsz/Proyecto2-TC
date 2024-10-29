import time
from help_methods import gr_reader, print_g, extraer_terminales, extraer_no_terminales
from CFG import eliminar_recursividad_izquierda, eliminar_epsilon, eliminar_unarias, eliminar_inutiles, procesar_terminales, convertir_a_cnf
from CYK import cyk_algorithm

def transformar_gramatica_a_cnf(gramatica, simbolo_inicial):
    """
    Transformar una gramática en su Forma Normal de Chomsky (CNF).
    :param gramatica: Diccionario con las producciones de la gramática.
    :param simbolo_inicial: Símbolo inicial de la gramática.
    :return: Gramática transformada a CNF.
    """

    #print("\nEliminando producciones epsilon...")
    #gramatica = eliminar_recursividad_izquierda(gramatica)
    #print_g(gramatica)

    print("\nEliminando producciones epsilon...")
    gramatica = eliminar_epsilon(gramatica)
    print_g(gramatica)

    print("\nEliminando producciones unitarias...")
    gramatica = eliminar_unarias(gramatica)
    print_g(gramatica)

    print("\nEliminando producciones inútiles...")
    gramatica = eliminar_inutiles(gramatica, simbolo_inicial)
    print_g(gramatica)

    no_terminales = extraer_no_terminales(gramatica)
    terminales = extraer_terminales(gramatica, no_terminales)

    print("\nProcesando terminales...")
    gramatica = procesar_terminales(terminales, gramatica, no_terminales)
    print_g(gramatica)

    print("\nConvirtiendo a Formal Normal de Chomsky...")
    gramatica = convertir_a_cnf(gramatica)

    print("\nTransformación a CNF completa.")
    return gramatica

file_path = "gramaticas.txt"
gramatica, simbolo_inicial = gr_reader(file_path)

start_time = time.time()
gramatica_cnf = transformar_gramatica_a_cnf(gramatica, simbolo_inicial)
end_time = time.time()

print_g(gramatica_cnf)
print(f"\nTiempo total para transformar la gramática a CNF: {end_time - start_time:.4f} segundos")

# Ingreso de múltiples cadenas
while True:
    try:
        word = input("\nIngresa una cadena de texto o escribe 'salir' para terminar: ")
        if word.lower() == "salir":
            print("Programa terminado.")
            break
        word = word.split()
        print(f"word = {word}")

        # Ejecutar el algoritmo CYK
        cyk_algorithm(word, gramatica_cnf, simbolo_inicial)

    except Exception as e:
        print(f"Ocurrió un error: {e}. Inténtalo nuevamente.")
