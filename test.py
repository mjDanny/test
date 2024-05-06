from flask import Flask, request, render_template, jsonify
from gradio_client import Client
import os

app = Flask(__name__)

# Инициализация клиента Gradio
client = Client("https://tonyassi-image-story-teller.hf.space/--replicas/m3hm6/")

# Путь для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Проверка, есть ли файл в запросе
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    # Если пользователь не выбрал файл, браузер может отправить пустой файл без имени.
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # Сохранение файла на сервере
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Вызов сервиса Gradio для предсказания
        try:
            result = client.predict(filename, api_name="/predict")
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)