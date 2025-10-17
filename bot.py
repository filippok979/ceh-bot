from flask import Flask, request
import requests
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "7420392791:AAF4_yGw2qHZ--aX6VTSyC5edb1zoL-9JX8"
ADMIN_CHAT_ID = "-4861255656"

# Основная клавиатура
main_keyboard = {
    "keyboard": [
        [{"text": "📁 Наши работы"}],
        [{"text": "💰 Рассчитать проект"}],
        [{"text": "🪵 Материалы и фурнитура"}],
        [{"text": "💬 Вопрос мастеру"}]
    ],
    "resize_keyboard": True
}

# Клавиатура для меню расчета проекта
calculation_keyboard = {
    "keyboard": [
        [{"text": "1. У меня есть Дизайн-Проект"}],
        [{"text": "2. Мне нужно помочь с реализацией моей идеи"}],
        [{"text": "3. Мне нужна мебель для моего бизнеса"}],
        [{"text": "🔙 Назад"}]
    ],
    "resize_keyboard": True
}

# Словарь для отслеживания состояния пользователей
user_states = {}

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

def send_to_admin(user, menu_type, message_text=None, file_info=None):
    """Отправка сообщения в админ чат"""
    user_name = user.get('first_name', 'Пользователь')
    username = f"@{user.get('username', 'нет')}" if user.get('username') else "нет"
    user_id = user.get('id', 'неизвестно')
    current_time = datetime.now().strftime("%H:%M %d.%m.%Y")
    
    message = (
        f"📞 🚨 {menu_type} 🚨\n"
        f"👤 Пользователь: {user_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 ID: {user_id}\n"
        f"⏰ Время: {current_time}\n"
    )
    
    if message_text:
        if len(message_text) > 1000:
            message_text = message_text[:1000] + "..."
        message += f"\n📝 Сообщение:\n{message_text}"
    
    if file_info:
        message += f"\n📎 Прикреплен файл/фото"
    
    send_message(ADMIN_CHAT_ID, message)

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
        
        # Проверяем, находится ли пользователь в состоянии ожидания ввода
        current_state = user_states.get(chat_id)
        
        if text == '/start':
            user_states[chat_id] = None
            send_message(chat_id, 
                "Привет! Я бот мастерской «ЦЕХ» 🛠️\n"
                "Выберите опцию ниже:",
                main_keyboard
            )
            send_message(ADMIN_CHAT_ID, f"🆕 Новый пользователь: {user_name}")
        
        elif text == '🔙 Назад':
            user_states[chat_id] = None
            send_message(chat_id, 
                "Главное меню:",
                main_keyboard
            )
        
        elif text == '📁 Наши работы':
            user_states[chat_id] = None
            send_message(chat_id, 
                "🛠️ Наши работы:\n\n"
                "https://disk.yandex.ru/d/IeeV4DCkWstadw",
                main_keyboard
            )
        
        elif text == '💰 Рассчитать проект':
            user_states[chat_id] = 'awaiting_calculation_choice'
            send_message(chat_id,
                "📊 Выберите тип проекта для расчета:",
                calculation_keyboard
            )
        
        # Обработка выбора в меню расчета
        elif current_state == 'awaiting_calculation_choice':
            if text == '1. У меня есть Дизайн-Проект':
                user_states[chat_id] = 'awaiting_design_project'
                send_message(chat_id,
                    "📎 Пожалуйста, прикрепите файл с дизайн-проектом и добавьте описание (если требуется).\n\n"
                    "Мы готовы рассмотреть ваш проект и предоставить расчет стоимости.",
                    calculation_keyboard
                )
            
            elif text == '2. Мне нужно помочь с реализацией моей идеи':
                user_states[chat_id] = 'awaiting_idea'
                send_message(chat_id,
                    "💡 Расскажите о вашей идее! Вы можете:\n"
                    "• Прикрепить фото/скриншоты\n"  
                    "• Описать ваши пожелания\n"
                    "• Указать примерные размеры\n\n"
                    "Мы поможем реализовать вашу задумку!",
                    calculation_keyboard
                )
            
            elif text == '3. Мне нужна мебель для моего бизнеса':
                user_states[chat_id] = 'awaiting_business'
                send_message(chat_id,
                    "🏢 Опишите ваши потребности в мебели для бизнеса:\n"
                    "• Тип мебели (стойки, витрины, столы и т.д.)\n"
                    "• Количество\n"
                    "• Особые требования\n"
                    "• Прикрепите фото/чертежи (если есть)\n\n"
                    "Мы предложим оптимальное решение!",
                    calculation_keyboard
                )
        
        # Обработка сообщений в состояниях ожидания
        elif current_state in ['awaiting_design_project', 'awaiting_idea', 'awaiting_business']:
            menu_types = {
                'awaiting_design_project': 'Дизайн-Проект',
                'awaiting_idea': 'Реализация идеи', 
                'awaiting_business': 'Мебель для бизнеса'
            }
            
            menu_type = menu_types.get(current_state, 'Расчет проекта')
            
            # Проверяем, есть ли файлы или фото
            file_info = None
            if 'document' in message:
                file_info = f"Документ: {message['document'].get('file_name', 'файл')}"
            elif 'photo' in message:
                file_info = "Фото"
            
            # Отправляем в админ чат
            send_to_admin(user, menu_type, text, file_info)
            
            # Подтверждаем пользователю
            send_message(chat_id,
                "✅ Ваша заявка принята! Мы свяжемся с вами в ближайшее время для уточнения деталей.",
                main_keyboard
            )
            
            # Сбрасываем состояние
            user_states[chat_id] = None
        
        elif text == '🪵 Материалы и фурнитура':
            user_states[chat_id] = None
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
            user_states[chat_id] = None
            send_message(chat_id,
                "👨‍🔧 Контакты: 8-903-656-34-80 @filippovceh",
                main_keyboard
            )
            send_message(ADMIN_CHAT_ID, f"🚨 {user_name} запросил контакт!")
        
        elif text and not current_state:
            # Игнорируем обычные текстовые сообщения (кроме состояний ожидания)
            send_message(chat_id, 
                "🤔 Я не понимаю это сообщение. Пожалуйста, используйте меню ниже:",
                main_keyboard
            )
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
