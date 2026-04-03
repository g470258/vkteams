# VK Teams Bot для Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/g470258/vkteams)

Интеграция для Home Assistant, позволяющая отправлять и получать сообщения через бота супераппа VK WorkSpace (VK Teams).

## 📋 Возможности

- ✅ Отправка текстовых сообщений
- ✅ Отправка фото и видео
- ✅ Инлайн-кнопки с обработкой callback'ов
- ✅ Редактирование и удаление сообщений
- ✅ Поддержка личных чатов и групп
- ✅ Long polling для получения событий
- ✅ Notify-сущности для каждого разрешённого чата
- ✅ Event-сущность для отслеживания событий
- ✅ Фильтрация сообщений по разрешённым чатам
- ✅ Поддержка HTML и MarkdownV2 форматирования


## 📦 Установка

### Через HACS (рекомендуется)

1. Установите [HACS](https://hacs.xyz/) если ещё не установлен
2. Добавьте пользовательский репозиторий:
   - Откройте HACS → Интеграции → ⋮ → Пользовательские репозитории
   - URL: `https://github.com/g470258/vkteams`
   - Категория: Интеграция
3. Нажмите "Установить"

### Вручную

1. Скачайте последний релиз из репозитория
2. Распакуйте папку `vkteams` в `/config/custom_components/`
3. Перезагрузите Home Assistant

## 🚀 Настройка

### Создание бота VK Teams

1. Найдите в VK Teams бота **@Metabot**
2. Отправьте команду `/newbot` и следуйте инструкциям
3. Сохраните полученный токен

### Добавление интеграции в Home Assistant

1. Перейдите в **Настройки** → **Устройства и сервисы** → **+ Добавить интеграцию**
2. Найдите **VK Teams Bot**
3. Введите:
   - **Токен бота** — полученный от @Metabot
   - **URL сервера** - для облачного использования, оставить без изменений. 
   - **Режим форматирования** — HTML или MarkdownV2 (по умолчанию HTML)
   - **Интервал опроса** — время ожидания событий (секунды)

### Добавление разрешённых чатов

После настройки бота:

1. На карточке интеграции нажмите кнопку **"+"**
2. Введите ID чата:
   - Для пользователя: `user@domain.ru` или `123456789`
   - Для группы: `123456789@chat.agent`
3. Бот будет отвечать только на сообщения из разрешённых чатов

> 💡 **Как узнать свой chat_id?** Напишите боту любое сообщение — он ответит с вашим chat_id.

## 📖 Использование

### Сервисы

| Сервис | Описание |
|--------|----------|
| `vkteams.send_message` | Отправка текстового сообщения |
| `vkteams.send_photo` | Отправка фото |
| `vkteams.send_video` | Отправка видео |
| `vkteams.edit_message` | Редактирование сообщения |
| `vkteams.delete_messages` | Удаление сообщений |
| `vkteams.answer_callback` | Ответ на callback от кнопки |

### Примеры автоматизаций

<details>
<summary><b>📝 Отправка простого сообщения</b></summary>

```yaml
action: vkteams.send_message
data:
  message: "Привет из Home Assistant!"
```
</details>

<details>
<summary><b>🎨 Отправка с заголовком и форматированием</b></summary>

```yaml
action: vkteams.send_message
data:
  message: "Текст сообщения"
  title: "Важное уведомление"
  parse_mode: "HTML"
```

Результат:
- Заголовок — **жирный**
- Текст — обычный
</details>

<details>
<summary><b>🔘 Отправка сообщения с инлайн-кнопками (горизонтально)</b></summary>

```yaml
action: vkteams.send_message
data:
  message: "Управление светом"
  buttons:
    - text: "💡 Включить"
      callbackData: "light_on"
      style: "primary"
    - text: "💡 Выключить"
      callbackData: "light_off"
      style: "secondary"
```

Результат: `[💡 Включить] [💡 Выключить]` (в одной строке)

Параметры кнопок:
- `text` — текст на кнопке
- `callbackData` — данные, возвращаемые при нажатии
- `style` — стиль подсвечивания кнопок: `default`(по умолчанию), `primary`, `secondary`, `danger`
</details>

<details>
<summary><b>🎛️ Сетка кнопок (матрица 3x3)</b></summary>

```yaml
action: vkteams.send_message
data:
  message: "Калькулятор:"
  buttons:
    - - text: "1"
        callbackData: "1"
      - text: "2"
        callbackData: "2"
      - text: "3"
        callbackData: "3"
    - - text: "4"
        callbackData: "4"
      - text: "5"
        callbackData: "5"
      - text: "6"
        callbackData: "6"
    - - text: "7"
        callbackData: "7"
      - text: "8"
        callbackData: "8"
      - text: "9"
        callbackData: "9"
    - - text: "0"
        callbackData: "0"
```

Результат:
```
[1][2][3]
[4][5][6]
[7][8][9]
[0]
```

Каждый вложенный массив — это отдельная строка кнопок.
</details>

<details>
<summary><b>🖼️ Отправка фото</b></summary>

```yaml
# Отправка локального файла
action: vkteams.send_photo
data:
  file: "/config/www/photo.png"
  caption: "Локальное фото"

# Отправка по URL
action: vkteams.send_photo
data:
  url: "https://example.com/photo.jpg"
  caption: "Фото из интернета"
```
</details>

<details>
<summary><b>🎬 Отправка видео</b></summary>

```yaml
# Отправка локального файла
action: vkteams.send_photo
data:
  file: "/config/www/video.mp4"
  caption: "Видео с камеры из локального файла"

# Отправка по URL
action: vkteams.send_video
data:
  url: "https://example.com/video.mp4"
  caption: "Видео с камеры из интернета"
```
> ⚠️ Ограничение 50 Мб на файл
</details>

<details>
<summary><b>✏️ Редактирование сообщения</b></summary>

```yaml
action: vkteams.edit_message
data:
  message_id: 123456789
  message: "Новый текст сообщения"
```
</details>

<details>
<summary><b>🗑️ Удаление сообщений</b></summary>

```yaml
action: vkteams.delete_messages
data:
  message_ids:
    - 123456789
    - 123456790
```

> ⚠️ Сообщения можно удалить только в течение 48 часов после отправки
</details>

### Обработка callback'ов от кнопок

При нажатии на кнопку генерируется событие `vkteams_callback` со следующими данными:

```yaml
trigger.event.data:
  query_id: "SVR:user@domain.ru:123456789:1234567890:12345-1234567890"
  callback_data: "light_on"
  chat_id: "user@domain.ru"
  user_id: "user@domain.ru"
  user_name: "Имя Фамилия"
  message:
    msgId: "1234567890"
    text: "Управление светом"
    timestamp: 1234567890
```

#### Доступные поля

| Поле | Описание |
|------|----------|
| `callback_data` | Данные, переданные в кнопке |
| `query_id` | Уникальный ID запроса (нужен для ответа) |
| `chat_id` | ID чата, откуда нажали кнопку |
| `user_id` | ID пользователя, который нажал |
| `user_name` | Имя и фамилия пользователя |
| `message.msgId` | ID исходного сообщения с кнопками |
| `message.text` | Текст исходного сообщения |

#### Примеры шаблонов

**Проверка значения callback_data:**
```yaml
conditions:
  - condition: template
    value_template: "{{ trigger.event.data.callback_data == 'light_on' }}"
```

**Извлечение ID пользователя:**
```yaml
variables:
  user_id: "{{ trigger.event.data.user_id }}"
  user_name: "{{ trigger.event.data.user_name }}"
```

**Удаление сообщения после нажатия:**
```yaml
action:
  - service: vkteams.delete_messages
    data:
      chat_id: "{{ trigger.event.data.chat_id }}"
      message_ids:
        - "{{ trigger.event.data.message.msgId | int }}"
```

**Ответ с указанием кто нажал:**
```yaml
action:
  - service: vkteams.send_message
    data:
      chat_id: "{{ trigger.event.data.chat_id }}"
      message: "Пользователь {{ trigger.event.data.user_name }} нажал кнопку {{ trigger.event.data.callback_data }}"
```

#### Полный пример автоматизации

```yaml
alias: "Управление светом через VK Teams"
trigger:
  - platform: event
    event_type: vkteams_callback
condition:
  - condition: template
    value_template: "{{ trigger.event.data.callback_data in ['light_on', 'light_off', 'light_status'] }}"
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.callback_data == 'light_on' }}"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.living_room
          - service: vkteams.answer_callback
            data:
              query_id: "{{ trigger.event.data.query_id }}"
              text: "✅ Свет включён"
              
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.callback_data == 'light_off' }}"
        sequence:
          - service: light.turn_off
            target:
              entity_id: light.living_room
          - service: vkteams.answer_callback
            data:
              query_id: "{{ trigger.event.data.query_id }}"
              text: "✅ Свет выключен"
              
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.callback_data == 'light_status' }}"
        sequence:
          - service: vkteams.send_message
            data:
              chat_id: "{{ trigger.event.data.chat_id }}"
              message: "Статус света: {{ states('light.living_room') }}"
          - service: vkteams.answer_callback
            data:
              query_id: "{{ trigger.event.data.query_id }}"
              text: "📊 Статус отправлен"
```

### Другие события

#### Событие `vkteams_command` (команды, начинающиеся с /)

```yaml
trigger:
  - platform: event
    event_type: vkteams_command
condition:
  - condition: template
    value_template: "{{ trigger.event.data.command == '/menu' }}"
```

Доступные поля:
- `command` — команда (например, `/menu`)
- `args` — аргументы команды
- `chat_id` — ID чата
- `user_id` — ID пользователя
- `user_name` — имя пользователя
- `text` — полный текст

#### Событие `vkteams_text` (обычный текст)

```yaml
trigger:
  - platform: event
    event_type: vkteams_text
```

Доступные поля:
- `text` — текст сообщения
- `chat_id` — ID чата
- `user_id` — ID пользователя
- `user_name` — имя пользователя
- `msg_id` — ID сообщения

#### Событие `vkteams_sent` (отправка сообщения ботом)

```yaml
trigger:
  - platform: event
    event_type: vkteams_sent
```

Доступные поля:
- `chat_id` — ID чата
- `message_id` — ID отправленного сообщения
- `text` — текст сообщения

### Notify-сущности

Для каждого разрешённого чата автоматически создаётся notify-сущность:

```yaml
action: notify.send_message
target:
  entity_id: notify.vkteams_user_at_domain_ru
data:
  message: "Уведомление через notify"
```

### Event-сущность

Основное устройство бота содержит event-сущность `Bot updates`, которая показывает последние события в своих атрибутах.

## 🛠️ Форматирование текста

### HTML режим

| Форматирование | Синтаксис | Пример |
|----------------|-----------|--------|
| Жирный | `<b>текст</b>` | `<b>Жирный</b>` |
| Курсив | `<i>текст</i>` | `<i>Курсив</i>` |
| Подчёркнутый | `<u>текст</u>` | `<u>Подчёркнутый</u>` |
| Зачёркнутый | `<s>текст</s>` | `<s>Зачёркнутый</s>` |
| Ссылка | `<a href="url">текст</a>` | `<a href="https://example.com">Ссылка</a>` |

### MarkdownV2 режим

| Форматирование | Синтаксис | Пример |
|----------------|-----------|--------|
| Жирный | `*текст*` | `*Жирный*` |
| Курсив | `_текст_` | `_Курсив_` |
| Подчёркнутый | `~текст~` | `~Подчёркнутый~` |
| Зачёркнутый | `-текст-` | `-Зачёркнутый-` |
| Ссылка | `[текст](url)` | `[Ссылка](https://example.com)` |

## ⚙️ Дополнительные параметры

### Отправка нескольким получателям

```yaml
action: vkteams.send_message
data:
  entity_id:
    - notify.vkteams_user1_at_domain_ru
    - notify.vkteams_user2_at_domain_ru
  message: "Всем привет!"
```

### Отправка в чат по прямому ID

```yaml
action: vkteams.send_message
data:
  chat_id: "user@domain.ru"
  message: "Привет!"
```

### Тихая отправка (без уведомления)

```yaml
action: vkteams.send_message
data:
  message: "Не беспокоить"
  disable_notification: true
```

## 🐛 Устранение неполадок

### Бот не отвечает на сообщения

1. Убедитесь, что chat_id добавлен в разрешённые через кнопку "+"
2. Проверьте логи Home Assistant на наличие ошибок
3. Убедитесь, что бот добавлен в группу (для групповых чатов)

### Не работают кнопки

1. Проверьте, что правильно указан `callbackData`
2. Убедитесь, что бот отвечает на callback (автоматически)

### Фото/видео не отправляются

1. Проверьте, что URL доступен из Home Assistant
2. Убедитесь, что файл не превышает лимиты VK Teams (до 50 МБ)

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

Приветствуются pull request'ы и issues на [GitHub](https://github.com/g470258/vkteams)
