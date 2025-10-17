from flask import Flask, request
import requests
import json

app = Flask(__name__)

BOT_TOKEN = "7420392791:AAF4_yGw2qHZ--aX6VTSyC5edb1zoL-9JX8"
ADMIN_CHAT_ID = "-4861255656"

# Клавиатура
main_keyboard = {
    "keyboard": [
        [{"text": "📁 Наши работы"}],
        [{"text": "💰 Рассчитать проект"}],
        [{"text": "🪵 Материалы и фурнитура"}],
        [{"text": "💬 Вопрос мастеру"}]
    ],
    "resize_keyboard": True
}

def send_message(chat_id, text, keyboard=None, parse_mode=None):
    """Отправка сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text
    }
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)
    if parse_mode:
        data['parse_mode'] = parse_mode
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response
    except:
        return None

@app.route('/')
def home():
    return "✅ Бот ЦЕХ работает! Используйте Telegram."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка вебхуков от Telegram"""
    update = request.get_json()
    
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message['from']
        
        user_name = user.get('first_name', 'Пользователь')
        
        if text == '/start':
            send_message(chat_id, 
                "Привет! Я бот мастерской «ЦЕХ» 🛠️\n"
                "Выберите опцию ниже:",
                main_keyboard
            )
            send_message(ADMIN_CHAT_ID, f"🆕 Новый пользователь: {user_name}")
        
        elif text == '📁 Наши работы':
            send_message(chat_id, 
                "🛠️ Наши работы:\n\n"
                "https://disk.yandex.ru/d/IeeV4DCkWstadw",
                main_keyboard
            )
        
        elif text == '💰 Рассчитать проект':
            send_message(chat_id,
                "📐 Расчет: 8-903-656-34-80 @filippovceh",
                main_keyboard
            )
            send_message(ADMIN_CHAT_ID, f"🚨 {user_name} запросил расчет!")
        
        elif text == '🪵 Материалы и фурнитура':
            send_message(chat_id,
                "🌳 <b>Материалы и фурнитура</b>\n\n"
                "📌 <b>ЛДСП:</b>\n"
                "🟫 <b>Lamarty</b>\n"
                "https://www.lamarty.ru/lamarty/decors/?ysclid=mgugeh3vew737907588\n\n"
                "🟫 <b>EGGER</b>\n"
                "https://basis-vrn.ru/ldsp-egger/?yclid=18235183174227066879\n\n"
                "🔩 <b>Фурнитура:</b>\n"
                "⚙️ <b>Blum</b>\n"
                "https://www.blum.com/md/ru/\n\n"
                "⚙️ <b>Boyard</b>\n"
                "https://www.boyard.biz/\n\n"
                "⚙️ <b>Hafele</b>\n"
                "https://hafele-shop.ru/?ysclid=mgugqk71pt831069121\n\n"
                "⚙️ <b>Hettich</b>\n"
                "https://hettich.ru/?ysclid=mgugrnesxl814262693\n\n"
                "📏 <b>Кромочный материал:</b>\n"
                "🎨 <b>Rehau</b>\n"
                "https://www.rehau.com/in-en/interiors-edges-edgebands",
                main_keyboard,
                parse_mode='HTML'
            )
        
        elif text == '💬 Вопрос мастеру':
            send_message(chat_id,
                "👨‍🔧 Контакты: 8-903-656-34-80 @filippovceh",
                main_keyboard
            )
            send_message(ADMIN_CHAT_ID, f"🚨 {user_name} запросил контакт!")
        
        elif text:
            # Обработка текстовых сообщений
            if len(text) > 4000:
                text = text[:4000] + "..."
            
            send_message(ADMIN_CHAT_ID, f"💬 {user_name}: {text}")
            send_message(chat_id, "✅ Сообщение получено!", main_keyboard)
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
