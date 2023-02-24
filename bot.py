import aiogram.types
from const_bot import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class Oplata(StatesGroup):
    contact = State()


n = 0
i = 0
next_button = aiogram.types.InlineKeyboardButton("Наступна сторінка", callback_data="next")
back_button = aiogram.types.InlineKeyboardButton("Попередня сторінка", callback_data="back")
view_cart_button = aiogram.types.KeyboardButton("Переглянути кошик")
oplata_button = aiogram.types.InlineKeyboardButton("Сплатити покупки", callback_data="oplata")
oplata_keyboard = aiogram.types.InlineKeyboardMarkup(resize_keyboard=True).add(oplata_button)


@dp.message_handler(commands=['start'])
async def сommands_start(message: aiogram.types.Message):
    keyboard_category = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for id_category, name in cur.execute("SELECT id, name FROM shop_category"):
        button_name = aiogram.types.KeyboardButton(str(name))
        keyboard_category.add(view_cart_button).row(button_name)
    await message.answer('Виберіть категорію', reply_markup=keyboard_category)


@dp.message_handler(content_types=['text'])
async def subcategory(message: aiogram.types.Message):
    keyboard_subcategory = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for id_category, name_category in cur.execute("SELECT id, name FROM shop_category"):
        if message.text == str(name_category):
            for id_subcategory, name_subcategory in cur.execute(
                    "SELECT id,name FROM shop_subcategory WHERE category_id = ?", [id_category]):
                button_name_subcategory = aiogram.types.KeyboardButton(str(name_subcategory))
                keyboard_subcategory.add(view_cart_button).add(button_name_subcategory)
                await message.answer('Виберіть підкатегорію', reply_markup=keyboard_subcategory)
    for id_subcategory, name_subcategory in cur.execute("SELECT id,name FROM shop_subcategory"):
        if message.text == str(name_subcategory):
            for id_product, name_product, description, price, image in cur.execute(
                    "SELECT id, name, description, price, image FROM shop_product WHERE subcategory_id = ? LIMIT 2 OFFSET ?",
                    [id_subcategory, n]):
                add_cart_button = aiogram.types.InlineKeyboardButton("Добавити у кошик",
                                                                     callback_data=f'add_cart{id_product}')
                add_like_button = aiogram.types.InlineKeyboardButton("Добавити у улюблені",
                                                                     callback_data=f'add_like{id_product}')
                navigation = aiogram.types.InlineKeyboardMarkup(resize_keyboard=True).add(add_cart_button).row(
                    back_button, next_button).add(add_like_button)
                await bot.send_message(message.chat.id,
                                       f"{name_product}\n"
                                       f"{description}\n"
                                       f"Вартість - {price} грн.\n", reply_markup=navigation)

    if message.text == 'Переглянути кошик':
        price_sum = 0
        id_product_list = []
        for id_cart_product, a in cur.execute("SELECT id,product_id FROM shop_cart WHERE user = ?",
                                              [message.from_user.username]):
            id_product_list.append(a)
        for id_p in id_product_list:
            for name_products, price, in cur.execute(
                    "SELECT  name, price FROM shop_product WHERE id = ?",
                    [id_p]):
                price_sum += price
                delete_cart_button = aiogram.types.InlineKeyboardButton("Видалити товар",
                                                                        callback_data=f"delete_cart{id_cart_product}")
                delete_cart_keyboard = aiogram.types.InlineKeyboardMarkup(resize_keyboard=True).add(delete_cart_button)

                await message.answer(f"Товар {name_products}\n"
                                     f"Вартість = {price}", reply_markup=delete_cart_keyboard)

        await message.answer(f"Загальна вартість = {price_sum}", reply_markup=oplata_keyboard)


@dp.callback_query_handler(lambda c: True)
async def button_handler(callback_query: aiogram.types.CallbackQuery):
    global n, i
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == 'next':
        n += 2
    elif callback_query.data == 'back':
        n -= 2
    elif 'add_cart' in callback_query.data or 'add_like' in callback_query.data:
        for id_product, name_product, description, price, image in cur.execute(
                "SELECT id, name, description, price, image FROM shop_product WHERE id = ?",
                [callback_query.data[-1]]):
            i += 1
            data = [
                (
                    i, 1 if 'add_cart' in callback_query.data else callback_query.data,
                    callback_query.from_user.username if 'add_cart' in callback_query.data else name_product,
                    id_product
                )
            ]
            cur.executemany("INSERT INTO shop_cart VALUES(?, ?, ?, ?)",
                            data) if 'add_cart' in callback_query.data else cur.executemany(
                "INSERT INTO shop_like VALUES(?, ?, ?, ?)", data)
            con.commit()
    elif 'delete_cart' in callback_query.data:
        sql = "DELETE FROM shop_cart WHERE id = ?"
        cur.execute(sql, [callback_query.data[-1]])
        con.commit()
    elif 'oplata' in callback_query.data:
        await Oplata.contact.set()
        await bot.send_message(callback_query.message.chat.id, f"Вкажіть номар телефона, або електрону почту")


@dp.message_handler(state=Oplata.contact)
async def contact(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        if '@' in message.text or len(message.text) == 10:
            data['contact'] = message.text
            print(data['contact'])
        else:
            await message.answer(f"Ви вказали не дійсні дані")
    await state.finish()


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)
