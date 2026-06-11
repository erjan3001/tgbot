from http.server import BaseHTTPRequestHandler
import json
import os
import telebot
from telebot import types

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_NAME = os.environ.get('CHANNEL_NAME')
MATERIAL_LINK = os.environ.get('MATERIAL_LINK')

# Укажите прямую ссылку на ваше изображение. 
# Вы также можете вынести её в Переменные окружения Vercel через os.environ.get
PHOTO_URL = 'https://i.ibb.co/cKYV6TWH/image.jpg' 

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_NAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Очищаем юзернейм от знака @ для ссылки
    clean_username = CHANNEL_NAME.replace("@", "")
    
    markup = types.InlineKeyboardMarkup()
    # Изменено: ссылка формата tg:// открывает канал сразу внутри приложения Telegram
    markup.add(types.InlineKeyboardButton('1. Подписаться на канал', url=f'tg://resolve?domain={clean_username}'))
    markup.add(types.InlineKeyboardButton('2. Проверить подписку', callback_data='check_sub'))
    
    welcome_text = (
        "Чтобы получить материалы, пожалуйста, подпишитесь на канал и вернитесь сюда после подписки. "
        "Нажмите кнопку проверки подписки и получите ссылку на материал."
    )
    
    # Изменено: теперь бот отправляет фото, а приветственный текст идет как подпись к нему
    bot.send_photo(message.chat.id, PHOTO_URL, caption=welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub(call):
    user_id = call.from_user.id
    if is_user_subscribed(user_id):
        bot.answer_callback_query(call.id, "Спасибо за подписку!")
        bot.send_message(call.message.chat.id, f"Ваша ссылка: {MATERIAL_LINK}")
    else:
        bot.answer_callback_query(call.id, "Вы еще не подписались!", show_alert=True)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body_json = json.loads(post_data.decode('utf-8'))
            update = telebot.types.Update.de_json(body_json)
            bot.process_new_updates([update])
        except Exception:
            pass
            
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')
