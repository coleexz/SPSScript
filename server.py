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
        user_input = data.get('input', None)  # Leer entrada del usuario si existe

        if not file_name or not file_content:
            return jsonify({"error": "El nombre y contenido del archivo son obligatorios"}), 400

        if not file_name.endswith('.sps'):
            return jsonify({"error": "El archivo debe tener la extensión '.sps'"}), 400

        # Escribir archivo temporalmente
        with open(file_name, "w") as temp_file:
            temp_file.write(file_content)
        print(f"Archivo {file_name} escrito con contenido:\n{file_content}")

        # Iniciar el intérprete en un proceso separado
        command = ["python3", "shell.py", file_name]
        process = subprocess.Popen(
            command,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Si hay input del usuario, enviarlo al proceso
        stdout, stderr = process.communicate(input=user_input if user_input else "")

        if "EOFError" in stderr:
            # Detectar si el intérprete está esperando input
            return jsonify({"awaiting_input": True, "output": stdout}), 200

        # Capturar salida del proceso
        return_code = process.returncode
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"Return Code: {return_code}")

        if return_code == 0:
            return jsonify({"output": stdout}), 200
        else:
            return jsonify({"error": stderr}), 500

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
