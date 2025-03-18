from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Función para transformar colores
def transformar_colores(image_path, old_color, new_color):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definir el rango de color a cambiar
    lower_bound = np.array(old_color[:3])
    upper_bound = np.array(old_color[3:])
    
    # Crear máscara para detectar el color seleccionado
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Suavizar la máscara para mejorar la detección
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    
    # Cambiar el color detectado al nuevo color
    image[mask > 0] = new_color
    
    # Guardar la imagen transformada
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.jpg')
    cv2.imwrite(output_path, image)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
            file.save(filepath)
            
            # Obtener colores del formulario
            old_h_min = int(request.form['old_h_min'])
            old_s_min = int(request.form['old_s_min'])
            old_v_min = int(request.form['old_v_min'])
            old_h_max = int(request.form['old_h_max'])
            old_s_max = int(request.form['old_s_max'])
            old_v_max = int(request.form['old_v_max'])
            
            new_r = int(request.form['new_r'])
            new_g = int(request.form['new_g'])
            new_b = int(request.form['new_b'])
            
            old_color = [old_h_min, old_s_min, old_v_min, old_h_max, old_s_max, old_v_max]
            new_color = [new_b, new_g, new_r]
            
            output_path = transformar_colores(filepath, old_color, new_color)
            return render_template('result.html', output_image='images/output.jpg')
    
    return render_template('index.html')

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)