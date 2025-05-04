from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def aplicar_filtro_color(image, old_rgb, new_color, tolerance=30):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Convertir el color objetivo a HSV
    color_hsv = cv2.cvtColor(np.uint8([[old_rgb[::-1]]]), cv2.COLOR_BGR2HSV)[0][0]
    
    # Crear rangos con tolerancia
    lower_bound = np.clip(color_hsv - np.array([tolerance, 50, 50]), 0, 255)
    upper_bound = np.clip(color_hsv + np.array([tolerance, 50, 50]), 0, 255)
    
    # Crear una máscara de todos los colores dentro del rango
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Para suavizar, aplicamos un difusor sobre la máscara
    blurred_mask = cv2.GaussianBlur(mask, (15, 15), 0)

    # Crear un nuevo color usando el color nuevo (solo cambiamos el matiz)
    new_color_hsv = cv2.cvtColor(np.uint8([[new_color[::-1]]]), cv2.COLOR_BGR2HSV)[0][0]
    
    # Asegurarnos de que la saturación y luminosidad no cambien
    hsv[blurred_mask > 0, 0] = new_color_hsv[0]

    # Convertimos de nuevo a BGR para obtener la imagen procesada
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return result

def transformar_colores(image_path, old_rgb, new_color, tolerance=30):
    image = cv2.imread(image_path)

    # Aplicamos el filtro para cambiar el color de forma gradual
    result = aplicar_filtro_color(image, old_rgb, new_color, tolerance)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')
    cv2.imwrite(output_path, result)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
            file.save(filepath)

            # Leer colores desde el formulario
            old_rgb = hex_to_rgb(request.form['old_rgb_min'])
            new_color = hex_to_rgb(request.form['new_rgb'])

            # Leer el valor de la tolerancia
            tolerance = int(request.form['tolerance'])

            output_path = transformar_colores(filepath, old_rgb, new_color, tolerance)
            return render_template('result.html', output_image='images/output.jpg')

    return render_template('index.html')

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)