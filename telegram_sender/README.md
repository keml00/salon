# ✈️ Telegram Salon Messenger

Десктоп-приложение для отправки сообщений клиентам в Telegram без сохранения их номера в контактах.

**by keml00, Telegram**

## Возможности

- 📱 Отправка по номеру телефона или @username
- 🤖 AI-форматирование текста (бесплатные модели через OpenRouter)
- 📋 История сообщений с экспортом в CSV/JSON
- 🎨 Современный тёмный интерфейс
- 🖥️ Кроссплатформенный (Windows/Linux/Mac)

## Установка

```bash
# 1. Клонировать
git clone https://github.com/keml00/salon.git
cd salon/telegram_sender

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env
cp .env.example .env
# Заполнить TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
# Получить на https://my.telegram.org

# 4. Запустить
python app.py
```

## Первый запуск

При первом запуске Telethon запросит код подтверждения из Telegram — введите его в терминале.
После этого создастся файл сессии и повторный ввод не потребуется.

## AI-форматирование

Для работы кнопки "Форматировать AI":
1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai)
2. Получите бесплатный API-ключ
3. Укажите `AI_API_KEY` в `.env`

Бесплатная модель: `meta-llama/llama-3-8b-instruct:free`

## Структура

```
telegram_sender/
├── app.py              # Главный файл GUI
├── telegram_client.py  # Модуль Telegram (Telethon)
├── ai_formatter.py     # AI-форматирование текста
├── history.py          # История сообщений
├── .env.example        # Пример конфигурации
└── requirements.txt    # Зависимости
```
