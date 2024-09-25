import os
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from googletrans import Translator
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.filters import Command

# Загрузка переменных из .env
load_dotenv()

# Получение API токенов
TOKEN = os.getenv("API_TOKEN")
THE_CAT_API_KEY = os.getenv("THE_CAT_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание роутера для хендлеров (обработчиков)
router = Router()

# Инициализация переводчика
translator = Translator()

# Создание клавиатуры с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("/joke")],
        [KeyboardButton("/cat")],
        [KeyboardButton("/nasa")],
        [KeyboardButton("/dog")],
        [KeyboardButton("/chuck")],
        [KeyboardButton("/weather")],
        [KeyboardButton("/trivia")]
    ],
    resize_keyboard=True
)


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


# Функция для перевода текста на русский
def translate_to_russian(text):
    translation = translator.translate(text, src='en', dest='ru')
    return translation.text


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


# Асинхронная функция для получения случайного вопроса викторины
async def get_trivia_question():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                trivia_data = await response.json()
                question = trivia_data['results'][0]['question']
                correct_answer = trivia_data['results'][0]['correct_answer']
                options = trivia_data['results'][0]['incorrect_answers'] + [correct_answer]
                random.shuffle(options)
                return question, options, correct_answer
    except Exception as e:
        return f"Не удалось получить вопрос викторины: {e}", [], ""


# Команда /start
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Вот что я могу:\n"
                         "/joke - Случайная шутка\n"
                         "/cat - Случайное фото кота\n"
                         "/nasa - Случайное космическое изображение\n"
                         "/dog - Случайное фото собаки\n"
                         "/chuck - Случайный факт о Чаке Норрисе\n"
                         "/weather <город> - Текущая погода\n"
                         "/trivia - Вопрос викторины",
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


# Команда /chuck для получения случайного факта о Чаке Норрисе
@router.message(Command("chuck"))
async def send_chuck_norris_fact(message: Message):
    chuck_fact = await get_chuck_norris_fact()  # Получаем случайный факт
    await message.answer(chuck_fact, reply_markup=keyboard)  # Отправляем факт


# Команда /weather для получения погоды
@router.message(Command("weather"))
async def send_weather(message: Message):
    city = message.get_args()  # Получаем аргумент команды (название города)
    if not city:
        await message.answer("Пожалуйста, укажите город. Например: /weather Москва", reply_markup=keyboard)
        return
    weather_info = await get_weather(city)
    await message.answer(weather_info, reply_markup=keyboard)


# Команда /trivia для получения вопроса викторины
@router.message(Command("trivia"))
async def send_trivia(message: Message):
    question, options, correct_answer = await get_trivia_question()
    if not question:
        await message.answer("Не удалось получить вопрос. Попробуйте позже.", reply_markup=keyboard)
        return
        options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
    await message.answer(f"Вопрос: {question}\n\nВарианты:\n{options_text}", reply_markup=keyboard)


# Регистрация роутера в диспетчере
dp.include_router(router)


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == 'main':
    asyncio.run(main())
