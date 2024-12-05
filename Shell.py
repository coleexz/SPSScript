import sys
import Run as Basic

def run_interactive_mode():
    """Modo interactivo de tu lenguaje."""
    while True:
        text = input('basic > ')
        if text.strip().lower() == 'exit':
            break
        result, error = Basic.run('<stdin>', text)
        if error:
            print(error.as_string())
        elif result:
            print(result)

def run_file(filename):
    try:
        with open(filename, 'r') as file:
            code = ''.join(line.strip() + '\n' for line in file if line.strip())
    except FileNotFoundError:
        print(f"Error: El archivo '{filename}' no existe.")
        sys.exit(1)

    result, error = Basic.run(filename, code)
    if error:
        print(error.as_string())
    elif result:
        print(result)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not filename.endswith('.sps'):
            print("Error: El archivo debe tener la extensión '.sps'.")
            sys.exit(1)
        run_file(filename)
    else:
        print("Bienvenido a Basic Interactive Shell. Escribe 'exit' para salir.")
        run_interactive_mode()
