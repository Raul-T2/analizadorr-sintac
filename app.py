from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definimos los tokens
tokens = [
    'INT', 'READ', 'PRINTF', 'END', 'PROGRAMA',  # Agregamos PROGRAMA como token
    'PARENTESIS_IZQUIERDA', 'PARENTESIS_DERECHA',
    'LLAVE_IZQUIERDA', 'LLAVE_DERECHA', 'PUNTO_Y_COMA', 
    'IDENTIFICADOR', 'IGUAL', 'SUMA', 'COMILLAS', 'STRING'
]

# Reglas de los tokens
t_PARENTESIS_IZQUIERDA = r'\('
t_PARENTESIS_DERECHA = r'\)'
t_LLAVE_IZQUIERDA = r'\{'
t_LLAVE_DERECHA = r'\}'
t_PUNTO_Y_COMA = r';'
t_IGUAL = r'='
t_SUMA = r'\+'
t_COMILLAS = r'\"'

# Diccionario de palabras reservadas
reserved = {
    'int': 'INT',
    'read': 'READ',
    'printf': 'PRINTF',
    'end': 'END',
    'programa': 'PROGRAMA'  # Movemos el token 'programa' aquí
}

# Añadimos la regla para reconocer "identificadores"
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFICADOR')  # Verifica si es una palabra reservada
    return t

# Cadenas de texto
def t_STRING(t):
    r'\".*?\"'
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Error de lexing: {t.value}")
    t.lexer.skip(1)

# Construimos el analizador léxico
lexer = lex.lex()

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    tabla_lexico = []
    tabla_sintactica = []
    tokens_totales = {"Tokens": 0, "Palabras Reservadas": 0, "Identificadores": 0, "Símbolos": 0, "Variables": 0}
    
    # Inicializamos una variable para el control de errores
    errores = []

    if request.method == "POST":
        text = request.form["text"]
        lexer.input(text)
        
        # Verificamos si el código ingresado coincide con el código principal
        lineas_codigo_principal = [
            "programa suma ( ) {",
            "int",
            "read a ;",
            "read b ;",
            "c = a + b ;",
            "printf ( \"la suma es\" );",
            "end ;",
            "}"
        ]
        
        # Variables para realizar la comprobación
        lineas_codigo = text.splitlines()
        
        # Detección de errores en el código ingresado
        for i, linea in enumerate(lineas_codigo):
            if i < len(lineas_codigo_principal):
                if linea.strip() != lineas_codigo_principal[i]:
                    errores.append(f"Error: Línea {i+1} modificada. Se esperaba: '{lineas_codigo_principal[i]}'")
        
        # Añadimos la lógica para la tabla léxica
        while True:
            tok = lexer.token()
            if not tok:
                break
            token_type = tok.type
            token_value = tok.value
            
            # Contar tokens por categoría
            tokens_totales["Tokens"] += 1
            if token_type in reserved.values():
                tokens_totales["Palabras Reservadas"] += 1
            elif token_type == 'IDENTIFICADOR':
                if token_value in ['a', 'b', 'c']:
                    tokens_totales["Variables"] += 1
                else:
                    tokens_totales["Identificadores"] += 1
            else:
                tokens_totales["Símbolos"] += 1

            # Lógica para la tabla léxica
            tabla_lexico.append((tok.lineno, token_type, token_value))

            # Lógica para la tabla sintáctica
            error_msg = ""
            if token_type not in tokens:
                error_msg = f"Error: Token inesperado '{tok.value}' en la línea {tok.lineno}"
            tabla_sintactica.append((tok.lineno, tok.value, error_msg if error_msg else "Correcto"))

        # Añadimos los errores detectados a la tabla sintáctica
        for error in errores:
            tabla_sintactica.append((len(tabla_sintactica) + 1, error, "Error"))  # Añadimos el error al final

    return render_template("index.html", 
                            tabla_lexico=tabla_lexico, 
                            tabla_sintactica=tabla_sintactica, 
                            text=text, 
                            tokens_totales=tokens_totales)

if __name__ == "__main__":
    app.run(debug=True)
