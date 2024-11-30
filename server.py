from flask import Flask, request, jsonify
import subprocess
import os
import flask_cors

app = Flask(__name__)
flask_cors.CORS(app)

@app.route('/run', methods=['POST'])
def run_script():
    try:
        # Leer datos del cliente
        data = request.json
        file_name = data.get('file_name')
        file_content = data.get('file_content')
        user_input = data.get('input', "")  # Leer entrada del usuario, si existe

        if not file_name or not file_content:
            return jsonify({"error": "El nombre y contenido del archivo son obligatorios"}), 400

        if not file_name.endswith('.sps'):
            return jsonify({"error": "El archivo debe tener la extensión '.sps'"}), 400

        # Escribir el archivo temporalmente
        with open(file_name, "w") as temp_file:
            temp_file.write(file_content)
        print(f"Archivo {file_name} escrito con contenido:\n{file_content}")

        # Ejecutar el comando
        command = ["python3", "shell.py", file_name]
        print(f"Ejecutando comando: {' '.join(command)}")

        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            input=user_input,  # Enviar la entrada del usuario al comando
            timeout=10  # Establecer un tiempo máximo de espera
        )

        # Capturar salida
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return_code = result.returncode

        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"Return Code: {return_code}")

        if return_code == 0:
            return jsonify({"output": stdout}), 200
        else:
            return jsonify({"error": stderr}), 500

    except subprocess.TimeoutExpired:
        print("Error: El proceso tomó demasiado tiempo y fue detenido.")
        return jsonify({"error": "El proceso tomó demasiado tiempo y fue detenido."}), 500

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
