import asyncio
import os
import random
from datetime import datetime, timedelta
import requests
from aiogram import Bot, Dispatcher
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from googletrans import Translator

# Загрузка переменных из .env
load_dotenv()

# Получение API токенов
TOKEN = os.getenv("TELEGRAM_TOKEN")
THE_CAT_API_KEY = os.getenv("THE_CAT_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание роутера для хендлеров (обработчиков)
router = Router()

# Инициализация переводчика
translator = Translator()


# Функция для получения случайной шутки
def get_random_joke():
    url = "https://v2.jokeapi.dev/joke/Any"
    response = requests.get(url)
    joke_data = response.json()

    if joke_data['type'] == 'single':
        return joke_data['joke']
    else:
        return f"{joke_data['setup']} - {joke_data['delivery']}"


# Функция для перевода текста на русский
def translate_to_russian(text):
    translation = translator.translate(text, src='en', dest='ru')
    return translation.text


# Функция для получения случайного изображения кота
def get_random_cat():
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": THE_CAT_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data[0]['url']


# Функция для получения случайного космического изображения
def get_random_nasa_image():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    date_str = random_date.strftime("%Y-%m-%d")

    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}"
    response = requests.get(url)
    data = response.json()
    return data['url'], data['title']


# Команда /start
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Вот что я могу:\n"
                         "/joke - Случайная шутка\n"
                         "/cat - Случайное фото кота\n"
                         "/nasa - Случайное космическое изображение")


# Команда /joke для получения и перевода шутки
@router.message(Command("joke"))
async def send_joke(message: Message):
    joke = get_random_joke()  # Получаем шутку на английском
    translated_joke = translate_to_russian(joke)  # Переводим шутку на русский
    await message.answer(translated_joke)  # Отправляем переведённую шутку


# Команда /cat для получения фото кота
@router.message(Command("cat"))
async def send_cat(message: Message):
    cat_image_url = get_random_cat()  # Получаем случайное изображение кота
    await message.answer_photo(photo=cat_image_url)  # Отправляем изображение


# Команда /nasa для получения космического изображения
@router.message(Command("nasa"))
async def send_nasa_image(message: Message):
    photo_url, title = get_random_nasa_image()  # Получаем изображение и заголовок
    await message.answer_photo(photo=photo_url, caption=title)  # Отправляем изображение и заголовок


# Регистрация роутера в диспетчере
dp.include_router(router)


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
