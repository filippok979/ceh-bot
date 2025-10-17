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

# Клавиатура для вопроса мастеру
question_keyboard = {
    "keyboard": [
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

def copy_to_admin(original_message, menu_type):
    """Копирование сообщения в админ чат с информацией"""
    user = original_message['from']
    user_name = user.get('first_name', 'Пользователь')
    username = f"@{user.get('username', 'нет')}" if user.get('username') else "нет"
    user_id = user.get('id', 'неизвестно')
    current_time = datetime.now().strftime("%H:%M %d.%m.%Y")
    
    # Информационное сообщение
    info_message = (
        f"📞 🚨 {menu_type} 🚨\n"
        f"👤 Пользователь: {user_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 ID: {user_id}\n"
        f"⏰ Время: {current_time}"
    )
    
    # Сначала отправляем информационное сообщение
    send_message(ADMIN_CHAT_ID, info_message)
    
    # Затем копируем контент оригинального сообщения
    text = original_message.get('text', '')
    caption = original_message.get('caption', '')
    
    if text:
        send_message(ADMIN_CHAT_ID, f"📝 Сообщение:\n{text}")
    
    if caption:
        send_message(ADMIN_CHAT_ID, f"📝 Описание:\n{caption}")
    
    # Обработка фото
    if 'photo' in original_message:
        photo = original_message['photo'][-1]  # Берем самое качественное фото
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'photo': photo['file_id']
        }
        if caption:
            data['caption'] = f"📎 Фото от {user_name}"
        try:
            requests.post(url, json=data, timeout=10)
        except:
            pass
    
    # Обработка документов
    elif 'document' in original_message:
        document = original_message['document']
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'document': document['file_id']
        }
        file_name = document.get('file_name', 'файл')
        data['caption'] = f"📎 Документ: {file_name} от {user_name}"
        try:
            requests.post(url, json=data, timeout=10)
        except:
            pass

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
        elif current_state in ['awaiting_design_project', 'awaiting_idea', 'awaiting_business', 'awaiting_question']:
            menu_types = {
                'awaiting_design_project': 'Дизайн-Проект',
                'awaiting_idea': 'Реализация идеи', 
                'awaiting_business': 'Мебель для бизнеса',
                'awaiting_question': 'Вопрос мастеру'
            }
            
            menu_type = menu_types.get(current_state, 'Сообщение')
            
            # Копируем сообщение в админ чат
            copy_to_admin(message, menu_type)
            
            # Подтверждаем пользователю
            send_message(chat_id,
                "✅ Ваше сообщение принято! Мастер свяжется с вами в ближайшее время.",
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
            user_states[chat_id] = 'awaiting_question'
            send_message(chat_id,
                "🎯 <b>Бесплатная консультация мастера</b>\n\n"
                "💬 Здесь вы можете получить бесплатную консультацию по любому вопросу, связанному с вашим будущим изделием:\n\n"
                "• 🤔 Не уверены в выборе материала или фурнитуры?\n"
                "• 📐 Есть сложности с планировкой или нестандартный размер?\n"
                "• 💡 Хотите услышать профессиональное мнение о вашем проекте?\n"
                "• 🧼 Нужен совет по уходу за мебелью?\n\n"
                "🛠️ Я помогу вам избежать ошибок и создать идеальную мебель для вашего дома. "
                "Просто напишите свой вопрос, я передам его мастеру и он с вами свяжется.",
                question_keyboard,
                parse_mode='HTML'
            )
        
        elif text and not current_state:
            # Игнорируем обычные текстовые сообщения (кроме состояний ожидания)
            send_message(chat_id, 
                "🤔 Я не понимаю это сообщение. Пожалуйста, используйте меню ниже:",
                main_keyboard
            )
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
