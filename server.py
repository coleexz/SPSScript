from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_script():
    try:
        data = request.json
        file_name = data.get('file_name')
        file_content = data.get('file_content')

        if not file_name or not file_content:
            return jsonify({"error": "El nombre y contenido del archivo son obligatorios"}), 400

        if not file_name.endswith('.sps'):
            return jsonify({"error": "El archivo debe tener la extensión '.sps'"}), 400

        # Escribir el archivo recibido en el servidor
        with open(file_name, "w") as temp_file:
            temp_file.write(file_content)

        # Ejecutar el comando
        command = ["python3", "shell.py", file_name]
        result = subprocess.run(command, text=True, capture_output=True)

        # Depuración en el servidor
        print(f"Comando ejecutado: {' '.join(command)}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        print(f"Return Code: {result.returncode}")

        # Verificar el resultado de la ejecución
        if result.returncode == 0:
            return jsonify({"output": result.stdout.strip()}), 200
        else:
            return jsonify({"error": result.stderr.strip()}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
