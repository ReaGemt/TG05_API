import os
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Загрузка переменных из .env
load_dotenv()

# Получение API токенов
TOKEN = os.getenv("TELEGRAM_TOKEN")
THE_CAT_API_KEY = os.getenv("THE_CAT_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание роутера для хендлеров (обработчиков)
router = Router()

# Создание клавиатуры с кнопками
keyboard_builder = ReplyKeyboardBuilder()
keyboard_builder.row(KeyboardButton(text="/joke"))
keyboard_builder.row(KeyboardButton(text="/cat"))
keyboard_builder.row(KeyboardButton(text="/nasa"))
keyboard_builder.row(KeyboardButton(text="/dog"))
keyboard_builder.row(KeyboardButton(text="/chuck"))
keyboard_builder.row(KeyboardButton(text="/weather"))

keyboard = keyboard_builder.as_markup(resize_keyboard=True)

# Функция для перевода текста на русский
def translate_to_russian(text):
    try:
        translation = GoogleTranslator(source='auto', target='ru').translate(text)
        return translation
    except Exception as e:
        return f"Ошибка перевода: {e}"

# Асинхронная функция для получения случайной шутки
async def get_random_joke():
    url = "https://v2.jokeapi.dev/joke/Any"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                joke_data = await response.json()
                if joke_data['type'] == 'single':
                    return joke_data['joke']
                else:
                    return f"{joke_data['setup']} - {joke_data['delivery']}"
    except Exception as e:
        return f"Не удалось получить шутку: {e}"

# Асинхронная функция для получения случайного изображения кота
async def get_random_cat():
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": THE_CAT_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data[0]['url']
    except Exception as e:
        return f"Не удалось получить изображение кота: {e}"

# Асинхронная функция для получения случайного космического изображения
async def get_random_nasa_image():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    date_str = random_date.strftime("%Y-%m-%d")

    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data['url'], data['title']
    except Exception as e:
        return f"Не удалось получить изображение NASA: {e}", ""

# Асинхронная функция для получения случайного изображения собаки
async def get_random_dog():
    url = "https://dog.ceo/api/breeds/image/random"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                dog_data = await response.json()
                return dog_data['message']  # URL изображения
    except Exception as e:
        return f"Не удалось получить изображение собаки: {e}"

# Асинхронная функция для получения случайного факта о Чаке Норрисе
async def get_chuck_norris_fact():
    url = "https://api.chucknorris.io/jokes/random"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                fact_data = await response.json()
                return fact_data['value']  # Текст шутки
    except Exception as e:
        return f"Не удалось получить факт о Чаке Норрисе: {e}"

# Асинхронная функция для получения текущей погоды
async def get_weather(city):
    api_key = OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                weather_data = await response.json()
                if weather_data.get('cod') != 200:
                    return f"Не удалось найти город: {city}"
                temp = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                return f"В {city} сейчас {temp}°C, {description}."
    except Exception as e:
        return f"Не удалось получить погоду: {e}"

# Команда /start
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Вот что я могу:\n"
                         "/joke - Случайная шутка\n"
                         "/cat - Случайное фото кота\n"
                         "/nasa - Случайное космическое изображение\n"
                         "/dog - Случайное фото собаки\n"
                         "/chuck - Случайный факт о Чаке Норрисе\n"
                         "/weather <город> - Текущая погода",
                         reply_markup=keyboard)

# Команда /joke для получения и перевода шутки
@router.message(Command("joke"))
async def send_joke(message: Message):
    joke = await get_random_joke()  # Получаем шутку на английском
    translated_joke = translate_to_russian(joke)  # Переводим шутку на русский
    await message.answer(translated_joke, reply_markup=keyboard)  # Отправляем переведённую шутку

# Команда /cat для получения фото кота
@router.message(Command("cat"))
async def send_cat(message: Message):
    cat_image_url = await get_random_cat()  # Получаем случайное изображение кота
    await message.answer_photo(photo=cat_image_url, reply_markup=keyboard)  # Отправляем изображение

# Команда /nasa для получения космического изображения
@router.message(Command("nasa"))
async def send_nasa_image(message: Message):
    photo_url, title = await get_random_nasa_image()  # Получаем изображение и заголовок
    await message.answer_photo(photo=photo_url, caption=title, reply_markup=keyboard)  # Отправляем изображение и заголовок

# Команда /dog для получения случайного изображения собаки
@router.message(Command("dog"))
async def send_dog(message: Message):
    dog_image_url = await get_random_dog()  # Получаем случайное изображение собаки
    await message.answer_photo(photo=dog_image_url, reply_markup=keyboard)  # Отправляем изображение

# Команда /chuck для получения случайного факта о Чаке Норрисе с переводом
@router.message(Command("chuck"))
async def send_chuck_norris_fact(message: Message):
    chuck_fact = await get_chuck_norris_fact()  # Получаем случайный факт о Чаке Норрисе на английском
    translated_fact = translate_to_russian(chuck_fact)  # Переводим факт на русский
    await message.answer(translated_fact, reply_markup=keyboard)  # Отправляем переведённый факт

# Команда /weather для получения погоды
@router.message(Command("weather"))
async def send_weather(message: Message):
    # Разделяем текст сообщения и получаем аргументы
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите город. Например: /weather Москва", reply_markup=keyboard)
        return

    city = args[1]  # Получаем название города
    weather_info = await get_weather(city)
    await message.answer(weather_info, reply_markup=keyboard)

# Регистрация роутера в диспетчере
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
