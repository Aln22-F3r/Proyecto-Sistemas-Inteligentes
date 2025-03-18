from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Función para transformar colores (ejemplo: azul a verde)
def transformar_colores(image_path):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definimos los colores que queremos cambiar (azul a verde)
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([140, 255, 255])

    # Detectamos el color azul
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Cambiamos el color azul a verde
    image[mask > 0] = [0, 255, 0]

    # Guardamos la nueva imagen
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')
    cv2.imwrite(output_path, image)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Guardar la imagen cargada
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
            file.save(filepath)

            # Aplicar la transformación
            output_path = transformar_colores(filepath)

            # Mostrar la imagen transformada
            return render_template('result.html', output_image='images/output.jpg')

    return render_template('index.html')

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)