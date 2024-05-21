import pandas as pd
import lexico

class node_stack:
    def __init__(self, symbol, lexeme):
        global count
        self.symbol = symbol
        self.lexeme = lexeme
        self.id = count
        count += 1

class node_tree:
    def __init__(self, id, symbol, lexeme):
        self.id = id
        self.symbol = symbol
        self.lexeme = lexeme
        self.children = []
        self.father = None

# Función para buscar un nodo en el árbol
def buscar_nodo(raiz, id): 
    if raiz.id == id:
        return raiz
    else:
        for hijo in raiz.children:
            resultado = buscar_nodo(hijo, id)
            if resultado is not None:
                return resultado
        return None

tabla = pd.read_csv("tablaV3.csv", index_col=0)
count = 0
stack = []


# Inicializar la pila con símbolos de inicio y fin
symbol_E = node_stack('INICIO', None)
symbol_dollar = node_stack('$', None)
stack.append(symbol_dollar)
stack.append(symbol_E)

# Configurar el árbol con el símbolo de inicio
root = node_tree(symbol_E.id, symbol_E.symbol, symbol_E.lexeme)

entrada = lexico.lexico('ejemplo2.txt')
#print(entrada)
index_entrada = 0

while len(stack) > 1:
    simbolo_entrada = entrada[index_entrada]["simbolo"]
    # Comparar la cima de la pila con el símbolo de entrada
    if stack[-1].symbol == simbolo_entrada:
        # Recuperamos el lexema.
        nodoActual = buscar_nodo(root, stack[-1].id)
        nodoActual.lexeme = entrada[index_entrada]["lexema"]
        
        print("Terminal:", stack[-1].symbol)
        stack.pop()
        index_entrada += 1
    else:
        if (stack[-1].symbol not in tabla.index
          or simbolo_entrada not in tabla.columns):
            print("-----------------Error en el proceso sintáctico1-----------------")
            print("ERROR CERCA A: ", entrada[index_entrada]["lexema"], "           En la linea: ", entrada[index_entrada]["nroline"])
            break
        # Obtener la producción de la tabla de análisis
        produccion = tabla.loc[stack[-1].symbol, simbolo_entrada]
        # Manejar errores de sintaxis
        if isinstance(produccion, float):
            print("-----------------Error en el proceso sintáctico2-----------------")
            print("ERROR CERCA A: ", entrada[index_entrada]["lexema"], "           En la linea: ", entrada[index_entrada]["nroline"])
            break

        # Aplicar la producción en la pila y el árbol
        if produccion != 'e':
            #print("Pila antes de aplicar producción:", [n.symbol for n in stack])
            #print("Producción:", produccion)
            #padre = buscar_nodo(stack[-1].id, root)
            node_x=stack.pop()
            for simbolo in reversed(str(produccion).split()):
                nodo_p = node_stack(simbolo, None)
                stack.append(nodo_p)
                hijo = node_tree(nodo_p.id, nodo_p.symbol, nodo_p.lexeme)  # Utiliza el lexema
                node_father = buscar_nodo(root, node_x.id)
                node_father.children.append(hijo)
                hijo.father = node_father
            print("Pila después de aplicar producción:", [n.symbol for n in stack])
        else:
            print("Pila antes de eliminar símbolo epsilon:", [n.symbol for n in stack])
            stack.pop()
            print("Pila después de eliminar símbolo epsilon:", [n.symbol for n in stack])


nombre_archivo = "arbol.txt"
archivo = open(nombre_archivo, "w")

def imprimir(nodo, padre=None):
    if nodo is not None:
        for hijo in reversed(nodo.children):
            imprimir(hijo, nodo)
        if padre is not None:

            if(nodo.lexeme == '<'):
                archivo.write(f"{nodo.id} [style = filled fillcolor= yellow label = <Symbol: {nodo.symbol}<BR/>Lexeme: 'menor a'>]\n")
            elif (nodo.lexeme == '>'):
                archivo.write(f"{nodo.id} [style = filled fillcolor= yellow label = <Symbol: {nodo.symbol}<BR/>Lexeme: 'mayor a'>]\n")
            else: 
                archivo.write(f"{nodo.id} [style = filled fillcolor= yellow label = <Symbol: {nodo.symbol}<BR/>Lexeme: '{nodo.lexeme}'>]\n")
                archivo.write(f"{padre.id} [style = filled fillcolor= brown label = <Symbol: {padre.symbol}<BR/>Lexeme: '{padre.lexeme}'>]\n")

            archivo.write(f"{padre.id} -> {nodo.id}\n")

if stack[-1].symbol == "$":
    print("\n\nSINTACTICO: CORRECTO")


# Funcion para registrar funciones en la tabla de simbolos
def registrar_funciones(nodo):
    if nodo is not None and nodo.symbol == "IDENTIFICADOR" and nodo.father.symbol == "FUNC":
        # Verificar si el nodo tiene al menos tres hijos
        ID= nodo.id 
        tipo_dato = "dinamico"
        nombre_funcion = nodo.lexeme 
        ambito = "global"
        codigo_flag = "FUNCION"
        stack.append({
            "ID": ID,
            "tipo_dato": tipo_dato,
            "nombre_funcion": nombre_funcion,
            "ambito": ambito,
            "codigo_flag": codigo_flag
        })
    elif nodo is not None and nodo.symbol == "IDENTIFICADOR" and nodo.father.symbol == "PARAMETRO":
        # Verificar si el nodo tiene al menos tres hijos
        ID= nodo.id 
        tipo_dato = nodo.father.children[-1].children[-1].lexeme
        nombre_funcion = nodo.lexeme 
        ambito = "funcion"
        codigo_flag = "variable"
        stack.append({
            "ID": ID,
            "tipo_dato": tipo_dato,
            "nombre_funcion": nombre_funcion,
            "ambito": ambito,
            "codigo_flag": codigo_flag
        })

    for hijo in nodo.children:
        registrar_funciones(hijo)





# Funcion para registrar variables en la tabla de simbolos
global ambit
ambit = "global"
def registrar_VARIABLES(nodo): 
    global ambit
    if nodo.symbol == "REGRESA":
        ambit = "funcion"
    if nodo is not None and nodo.symbol == "IDENTIFICADOR" and nodo.father.symbol == "DECLARACION":
        # Verificar si el nodo tiene al menos tres hijos

        ID= nodo.id 
        tipo_dato = nodo.symbol 
        nombre_variable = nodo.lexeme 
        ambito = ambit
        codigo_flag = "VARIABLE"
        stack.append({
            "ID": ID,
            "tipo_dato": tipo_dato,
            "nombre_variable": nombre_variable,
            "ambito": ambito,
            "codigo_flag": codigo_flag
        })

    for hijo in nodo.children:
        registrar_VARIABLES(hijo)



# Llamada a la funcion para registrar variables
registrar_funciones(root)
# Llamada a la funcion para registrar variables
registrar_VARIABLES(root)

# Imprimir la tabla de simbolos
print("Tabla de Símbolos:")
for simbolo in stack:
    print(simbolo)


archivo.write("digraph G {\n")
imprimir(root)
#print("}")
archivo.write("}\n")
archivo.close()