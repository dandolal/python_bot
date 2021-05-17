import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from response import Response
from aiogram.utils.markdown import text, bold, italic

bot = Bot(token='1886047684:AAEx2ys4YeOkz1tCt9B2ggp4_AM5vKZ3cF4')
dp = Dispatcher(bot)
response = dict()
query = ''


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.from_user.id not in response.keys():
        response[message.from_user.id] = Response()
    await message.reply("Привет!\nЯ бот, который поможет тебе в поиске информации о фильме.\n Введите название фильма.")


@dp.message_handler(regexp=r"\/i\d+")
async def click_id_handle(message: types.Message):
    if message.from_user.id not in response.keys():
        response[message.from_user.id] = Response()
    keyboard = types.InlineKeyboardMarkup()
    watch_button = types.InlineKeyboardButton(text="Смотреть онлайн", callback_data="watch")
    keyboard.add(watch_button)

    async with aiohttp.ClientSession() as cur_session:
        await response[message.from_user.id].response_id_query(cur_session, int(message['text'][2:]))
        resp, photo = response[message.from_user.id].description, response[message.from_user.id].photo

    if photo is not None:
        await message.answer("[ ]({}) {}".format(photo, resp),
                             parse_mode='markdown', reply_markup=keyboard)
    else:
        await message.answer(resp, reply_markup=keyboard)


@dp.message_handler(content_types=["text"])
async def query_handle(message: types.Message):
    if message.from_user.id not in response.keys():
        response[message.from_user.id] = Response()
    async with aiohttp.ClientSession() as cur_session:
        resp = await response[message.from_user.id].get_films_by_name(cur_session, message.text.lower())
        keyboard = types.InlineKeyboardMarkup()
        for movie in resp.split('\n')[1:]:
            if len(movie) == 0:
                continue
            movie_info = movie.split('\t')
            print(movie_info)
            await response[message.from_user.id].set_query(message.text.lower())

            film_button = types.InlineKeyboardButton(text=' '.join(movie_info[:2]),
                                                      callback_data="film_info\t{}".format(movie_info[2]))
            keyboard.add(film_button)
        await message.answer(resp.split('\n')[0], reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True)
async def click_button_handle(call: types.CallbackQuery):
    if call.message:
        keyboard = types.InlineKeyboardMarkup()
        data = call.data.split('\t')
        print(data)
        if data[0] == 'film_info':
            await response[call.from_user.id].set_movie_info(data[1])
            query = await response[call.from_user.id].get_query()
            back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
            print(query)

            watch_button = types.InlineKeyboardButton(text="Смотреть онлайн", callback_data="watch")


            async with aiohttp.ClientSession() as cur_session:
                id = await response[call.from_user.id].get_movie_info()
                await response[call.from_user.id].response_id_query(cur_session, int(id))
                resp, photo = response[call.from_user.id].description, response[call.from_user.id].photo

            keyboard.add(watch_button)
            keyboard.add(back_button)
            if photo is not None:
                await call.message.answer("[ ]({}) {}".format(photo, resp),
                                     parse_mode='markdown', reply_markup=keyboard)
            else:
                await call.message.answer(resp, reply_markup=keyboard)
        if data[0] == 'back':
            async with aiohttp.ClientSession() as cur_session:
                query = await response[call.from_user.id].get_query()
                resp = await response[call.from_user.id].get_films_by_name(cur_session, query)
                for movie in resp.split('\n')[1:]:
                    if len(movie) == 0:
                        continue
                    movie_info = movie.split('\t')
                    film_button = types.InlineKeyboardButton(text=' '.join(movie_info[:2]),
                                                              callback_data="film_info\t{}".format(movie_info[2]))
                    keyboard.add(film_button)
                await call.message.answer(resp.split('\n')[0], reply_markup=keyboard)

        if data[0] == "watch":
            back_button = types.InlineKeyboardButton(text="Назад", callback_data="back_to_film")
            ivi_button = types.InlineKeyboardButton(text="IVI", url="https://www.ivi.ru/search/?q=" + response[call.from_user.id].title)
            okko_button = types.InlineKeyboardButton(text="OKKO", url="https://okko.tv/search/" + response[call.from_user.id].title)
            kp_button = types.InlineKeyboardButton(text="KINOPOISK", url="https://www.kinopoisk.ru/index.php?kp_query=" + response[call.from_user.id].title)
            keyboard.add(ivi_button, okko_button, kp_button, back_button)
            await call.message.edit_text(text=text(bold('Смотреть онлайн')), reply_markup=keyboard)

        if data[0] == 'back_to_film':
            back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")

            watch_button = types.InlineKeyboardButton(text="Смотреть онлайн",
                                                      callback_data="watch")

            async with aiohttp.ClientSession() as cur_session:
                id = await response[call.from_user.id].get_movie_info()
                await response[call.from_user.id].response_id_query(cur_session, int(id))
                resp, photo = response[call.from_user.id].description, response[call.from_user.id].photo

            keyboard.add(watch_button)
            keyboard.add(back_button)
            if photo is not None:
                await call.message.answer("[ ]({}) {}".format(photo, resp),
                                          parse_mode='markdown', reply_markup=keyboard)
            else:
                await call.message.answer(resp, reply_markup=keyboard)

if __name__ == '__main__':
    executor.start_polling(dp)
