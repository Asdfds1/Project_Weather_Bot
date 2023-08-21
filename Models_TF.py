import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from PIL import Image, ImageOps
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow import keras
import numpy as np
import cv2

def load_or_create_model_tf():
    try:
        model = load_model('My_model.h5')
        return model
    except BaseException as e:
        # Загрузка набора данных Fashion MNIST
        fashion_mnist = tf.keras.datasets.fashion_mnist
        (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
        train_images = train_images.reshape(train_images.shape[0], 28, 28, 1)
        test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)
        input_shape = (28, 28, 1)

        # Нормализация изображений
        train_images = train_images / 255.0
        test_images = test_images / 255.0

        # Определение модели
        model = keras.Sequential([
            keras.layers.Conv2D(48, (3, 3), activation='relu', input_shape=(28, 28, 1)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(128, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(10, activation='softmax')
        ])

        # Компиляция модели
        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        # Обучение модели
        model.fit(train_images, train_labels, epochs=20, verbose=1)

        # Оценка точности модели на тестовых данных
        test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
        print('\nТочность на тестовых данных:', test_acc)
        model.save('My_model.h5')
        return model

def predict(model,photo):
    try:
        photo.thumbnail((28, 28))
        height, width = photo.size
        if width > height:
            delta = (width - height)
            padding = (delta, 0, 0, 0)
        else:
            delta = (height - width)
            padding = (0, delta, 0, 0)
        photo_padded = ImageOps.expand(photo, padding, fill=0)
        photo = np.array(photo_padded)
        print(photo.shape)

        # Изменение размера изображения до 28x28
        photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)

        img = Image.fromarray(photo)
        # сохраняем изображение
        img.save('image.png')
        # Нормализация изображения
        image_normalized = photo / 255.0

        # Добавление размерности для подачи в модель
        image_normalized = tf.expand_dims(image_normalized, axis=0)

        # Получение предсказания модели
        prediction = model.predict(image_normalized)

        predicted_class_index = np.argmax(prediction)

        class_names = ['футболка', 'брюки', 'свитер', 'платье', 'куртка', 'туфли', 'рубашка', 'кроссовки', 'сумка',
                       'ботинки']
        predicted_class_name = class_names[predicted_class_index]
        print(predicted_class_name)
        print(predicted_class_index)
        print(prediction)

        return predicted_class_name
    except BaseException as e:
        print(e)
        return None