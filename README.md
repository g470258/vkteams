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
<summary><b>🔘 Отправка сообщения с инлайн-кнопками</b></summary>

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
  buttons_layout: "row"
```

Параметры кнопок:
- `text` — текст на кнопке
- `callbackData` — данные, возвращаемые при нажатии
- `style` — стиль: `default`, `primary`, `secondary`, `danger`
- `buttons_layout` — расположение: `row` (горизонтально) или `column` (вертикально)
</details>

<details>
<summary><b>🖼️ Отправка фото</b></summary>

```yaml
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
action: vkteams.send_video
data:
  url: "https://example.com/video.mp4"
  caption: "Видео с камеры"
```
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

```yaml
alias: "Обработка кнопок VK Teams"
trigger:
  - platform: event
    event_type: vkteams_callback
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
```

### События

| Событие | Описание |
|---------|----------|
| `vkteams_callback` | Нажатие на инлайн-кнопку |
| `vkteams_command` | Получение команды (начинается с /) |
| `vkteams_text` | Получение текстового сообщения |
| `vkteams_sent` | Отправка сообщения ботом |

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
