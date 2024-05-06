from flask import Flask, request, render_template
import os
import cv2
import random
from gradio_client import Client

app = Flask(__name__)

# Инициализация клиента Gradio
client = Client("https://tonyassi-image-story-teller.hf.space/--replicas/m3hm6/")

# Путь для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_random_frame(video_path):
    # Открываем видеофайл
    cap = cv2.VideoCapture(video_path)
    # Получаем общее количество кадров в видео
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Выбираем случайный кадр
    random_frame_number = random.randint(0, total_frames - 1)
    # Устанавливаем кадр в видео по номеру
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)
    # Читаем кадр
    ret, frame = cap.read()
    # Закрываем видеофайл
    cap.release()
    # Возвращаем случайный кадр
    return frame


@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Проверка, есть ли файл в запросе
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    # Если пользователь не выбрал файл, браузер может отправить пустой файл без имени.
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Сохранение файла на сервере
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Выбор случайного кадра из видео
        random_frame = get_random_frame(filename)
        # Сохранение кадра в файл
        output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'random_frame.jpg')
        cv2.imwrite(output_filename, random_frame)

        # Вызов сервиса Gradio для предсказания
        try:
            result = client.predict(output_filename, api_name="/predict")
            # Вывод результата на странице
            return render_template('result.html', result=result)
        except Exception as e:
            return str(e), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
