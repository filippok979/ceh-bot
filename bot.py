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
    
    # Создаем клавиатуру с кнопками для админа
    admin_keyboard = {
        "inline_keyboard": [
            [
                {"text": "📋 Скопировать ID", "callback_data": f"copy_{user_id}"},
                {"text": "💌 Ответить", "callback_data": f"reply_{user_id}"}
            ]
        ]
    }
    
    # Информационное сообщение
    info_message = (
        f"📞 🚨 {menu_type} 🚨\n"
        f"👤 Пользователь: {user_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 ID: {user_id}\n"
        f"⏰ Время: {current_time}"
    )
    
    # Сначала отправляем информационное сообщение с кнопками
    send_message(ADMIN_CHAT_ID, info_message, admin_keyboard)
    
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

def handle_callback_query(callback_query):
    """Обработка нажатий на inline-кнопки"""
    data = callback_query['data']
    user_id = callback_query['from']['id']
    message_id = callback_query['message']['message_id']
    
    if data.startswith('copy_'):
        target_user_id = data.replace('copy_', '')
        # Отправляем админу ID для копирования
        send_message(user_id, f"🆔 ID пользователя: `{target_user_id}`\n\nСкопируйте этот ID для ответа.", parse_mode='Markdown')
        
    elif data.startswith('reply_'):
        target_user_id = data.replace('reply_', '')
        # Инструкция для ответа пользователю
        send_message(user_id, 
            f"✉️ Ответ пользователю ID: `{target_user_id}`\n\n"
            f"Чтобы отправить сообщение, используйте команду:\n"
            f"`/send {target_user_id} Ваш текст сообщения`\n\n"
            f"Например:\n"
            f"`/send {target_user_id} Здравствуйте! Получили ваше сообщение.`",
            parse_mode='Markdown'
        )
    
    # Подтверждаем обработку callback (убирает "часики")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={'callback_query_id': callback_query['id']})

def handle_admin_command(message):
    """Обработка команд админа"""
    text = message.get('text', '')
    admin_id = message['from']['id']
    
    if text.startswith('/send '):
        parts = text.split(' ', 2)
        if len(parts) >= 3:
            target_user_id = parts[1]
            message_text = parts[2]
            
            try:
                # Пытаемся отправить сообщение пользователю
                send_message(target_user_id, 
                    f"💬 Сообщение от мастера:\n\n{message_text}\n\n"
                    f"✉️ Чтобы ответить, просто напишите в этот чат."
                )
                send_message(admin_id, f"✅ Сообщение отправлено пользователю {target_user_id}")
            except:
                send_message(admin_id, f"❌ Не удалось отправить сообщение пользователю {target_user_id}")
        else:
            send_message(admin_id, "❌ Используйте: /send USER_ID ТЕКСТ_СООБЩЕНИЯ")
        
        return True
    
    return False

@app.route('/')
def home():
    return "✅ Бот ЦЕХ работает! Используйте Telegram."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка вебхуков от Telegram"""
    update = request.get_json()
    
    # Обработка callback_query (нажатий на кнопки)
    if 'callback_query' in update:
        handle_callback_query(update['callback_query'])
        return 'OK'
    
    if 'message' in update:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message['from']
        
        user_name = user.get('first_name', 'Пользователь')
        
        # Проверяем, является ли отправитель админом и обрабатываем команды
        if str(chat_id) == ADMIN_CHAT_ID.replace('-', ''):
            if handle_admin_command(message):
                return 'OK'
        
        # Проверяем, находится ли пользователь в состоянии ожидания ввода
        current_state = user_states.get(chat_id)
        
        if text == '/start':
            user_states[chat_id] = None
            send_message(chat_id, 
                "Привет! Я бот мастерской «ЦЕХ» 🛠️\n"
                "Выберите опцию ниже:",
                main_keyboard
            )
            # Обновляем уведомление для админа с кнопками
            user_id = user.get('id', 'неизвестно')
            username = f"@{user.get('username', 'нет')}" if user.get('username') else "нет"
            admin_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "📋 Скопировать ID", "callback_data": f"copy_{user_id}"},
                        {"text": "💌 Ответить", "callback_data": f"reply_{user_id}"}
                    ]
                ]
            }
            send_message(ADMIN_CHAT_ID, 
                f"🆕 Новый пользователь: {user_name}\n"
                f"📱 Username: {username}\n"
                f"🆔 ID: {user_id}", 
                admin_keyboard
            )
        
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
                "🚪 <b>Фасады в эмали и пленке ПВХ</b>\n\n"
                "📌 <b>ЛДСП:</b>\n"
                "🟫 <b>Lamarty</b>\n"
                "https://www.lamarty.ru/lamarty/\n\n"
                "🟫 <b>EGGER</b>\n"
                "https://egger-russia.ru/\n\n"
                "🔩 <b>Фурнитура:</b>\n"
                "⚙️ <b>Blum</b>\n"
                "https://www.blum.com/md/ru/\n\n"
                "⚙️ <b>Boyard</b>\n"
                "https://www.boyard.biz/\n\n"
                "⚙️ <b>Hafele</b>\n"
                "https://hafele-shop.ru/\n\n"
                "⚙️ <b>Hettich</b>\n"
                "https://hettich.ru/\n\n"
                "📏 <b>Кромочный материал:</b>\n"
                "🎨 <b>Rehau</b>\n"
                "https://www.rehau.com/in-en\n\n"
                "✨ <b>Смарт-материал:</b>\n"
                "🌟 <b>Fenix-hpl</b>\n"
                "https://fenix-hpl.ru/\n\n"
                "🎨 <b>Декоративные панели:</b>\n"
                "🟨 <b>Kastamonu</b>\n"
                "https://www.kastamonuentegre.com/ru_ru/tovary/dekorativnye-paneli\n\n"
                "🟫 <b>Woodstock</b>\n"
                "https://www.woodstock.su/\n\n"
                "🛡️ <b>Столешницы</b>\n\n"
                "🛡️ <b>HPL-Compact</b>\n"
                "https://arcoplastica.ru/\n\n"
                "💎 <b>Акриловый и натуральный камень</b>\n"
                "https://akvrn.ru/?ysclid=mgupb00w9b365927187\n\n"
                "⬜ <b>ДСП</b>\n"
                "https://amk-troya.ru/product-category/stoleshniczy/",
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
