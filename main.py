import telebot
import sqlite3
from telebot.types import *

con = sqlite3.connect("db.sqlite", check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

bot = telebot.TeleBot("5626175322:AAEG7TO71y0txX7jfnd0OP2b20aMrdquD7I", parse_mode="html")

psycholog = 5047068510

@bot.message_handler(content_types=['text'])
def text_message_handler(message):
    cur.execute("SELECT user_id FROM queue")
    queue = cur.fetchall()
    for i in queue:
        inQueue = True if message.from_user.id in list(i) else False
        if inQueue:
            break

    if message.from_user.id == psycholog:
        cur.execute("SELECT user_id FROM queue WHERE num")
        res = dict(cur.fetchall()[0])

        bot.send_message(res['user_id'], f"<b>Сообщение от психолога </b>\n<i>> {message.text}</i>")

    if inQueue:
        cur.execute(f"SELECT * FROM queue WHERE user_id = {message.from_user.id}")
        res = [dict(row) for row in cur.fetchall()]
        if res[0]['num'] == 1:
            if message.text == "Закончить диалог":
                cur.execute(f"DELETE FROM queue WHERE user_id = {message.from_user.id}")         
                cur.execute("UPDATE queue SET num = num - 1 WHERE num != 0")
                con.commit()

                cur.execute("SELECT user_id FROM queue WHERE num = 1")
                bot.send_message(message.from_user.id, "<b>Диалог окончен!</b>")

                try:
                    res = dict(cur.fetchall()[0])
                    bot.send_message(res['user_id'], "<b>Диалог начат!</b>")
                    bot.send_message(psycholog, f"<b>Диалог с #id{int(res['user_id'])*2} начат!</b>")
                except:
                    return
                return
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(
                "Пожаловаться", callback_data=f"report_{message.from_user.id}"))
            bot.send_message(psycholog, f"<b>Сообщение от #id{int(message.from_user.id*2)}</b>\n<i>> "+message.text+"</i>", reply_markup=markup)
        return        

    if message.text == "/start":
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton(
            "Начать диалог", callback_data=f"addToQueue"))
        bot.send_message(message.from_user.id, "Нажимая 'Начать диалог' вы соглашаетесь с <a href='t.me'><b>правилами</b></a> и <a href='t.me'><b>политикой конфиденциальности бота</b></a>", reply_markup=markup, disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "addToQueue":
        cur.execute("SELECT * FROM queue")
        res = [dict(row) for row in cur.fetchall()]
        for i in res:
            if i['user_id'] == call.from_user.id:
                bot.send_message(call.from_user.id, "<b>Вы уже в очереди!</b>")
                return
        cur.execute(f"INSERT INTO queue VALUES ({res[-1]['num']+1}, {call.from_user.id})")
        con.commit()
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=f"<b>Вы добавлены в очередь!\nВаш номер: {len(res)}</b>")
        if len(res) == 1:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Закончить диалог"))
            bot.send_message(call.from_user.id, "<b>Диалог начат!</b>", reply_markup=markup)
            bot.send_message(psycholog, f"<b>Диалог с #id{int(call.from_user.id)*2} начат!</b>")
bot.polling(non_stop=True)