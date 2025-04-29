import os
import random
import asyncio
import requests
import json
from datetime import datetime
from telegram import Bot, PollType
from telegram.constants import ParseMode


# Настройки
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
CHANNEL_USERNAME = "@altynmaturuen"  # Название твоего канала

LOG_FILE = "published_posts.json"
POST_TOPICS = [
    "Лайфхак для Valorant: как улучшить позиционирование",
    "Почему Half-Life 3 никогда не выйдет?",
    "10 игр, где можно потерять часы — но всё равно не пройти до конца",
    "Где найти крутые моды для Skyrim после 10 лет игры",
    "Как собрать бюджетный игровой ПК в 2025 году?",
    "Игры с мультиплеером, которые стоит попробовать",
    "Неожиданные фишки в Minecraft, о которых ты не знал"
]

POLL_QUESTIONS = [
    ("Какую платформу используешь чаще?", ["PC", "PS5", "Xbox", "Switch"]),
    ("Любишь локализации?", ["Да", "Нет", "Мне всё равно"]),
    ("Любимый жанр?", ["Шутеры", "Ролевые", "Стратегии", "Выживалки"]),
    ("Играешь больше в одиночку или в коопе?", ["Соло", "Кооп", "Мультиплеер"]),
]


# =================== ФУНКЦИИ ==================== #

def load_published():
    """Загружаем уже опубликованные посты"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_published(post_id):
    """Сохраняем новый пост как опубликованный"""
    posts = load_published()
    posts.append({"id": post_id, "time": str(datetime.now())})
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2)


def get_steam_free_game():
    try:
        response = requests.get("https://store.steampowered.com/api/featuredgames").json()
        game = response["freegames"][0]
        return {
            "title": game['name'],
            "id": game['id'],
            "link": f"https://store.steampowered.com/app/{game['id']}",
            "type": "steam"
        }
    except Exception as e:
        print(f"[Ошибка] Не могу получить игру из Steam: {e}")
        return None


def get_epic_free_game():
    try:
        response = requests.get(
            "https://store-site-backend-static.ak.epicgames.com/freeGamePromotions?country=US&language=en-US&allowCountries=US"
        ).json()
        game = response["data"]["Catalog"]["searchStore"]["elements"][0]
        return {
            "title": game['title'],
            "id": game['id'],
            "link": f"https://store.epicgames.com/en-US/p/{game['productSlug']}",
            "type": "epic"
        }
    except Exception as e:
        print(f"[Ошибка] Не могу получить игру из Epic: {e}")
        return None


def generate_post(topic=None, game=None):
    greetings = [
        "🔥 Снова раздача!",
        "🎮 Кто хочет халявы?",
        "💥 Лови момент!",
        "🎁 Сегодня можно забрать:"
    ]

    signoffs = [
        "👉 Скорее переходи по ссылке.",
        "⏳ Раздача активна ограниченное время.",
        "✅ Просто зайди и забери.",
        "💡 Посмотри трейлер перед скачкой."
    ]

    greeting = random.choice(greetings)
    signoff = random.choice(signoffs)

    if game and game['type'] == "steam":
        name = game['title']
        link = game['link']

        image_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['id']}/header.jpg"

        text = f"""
{greeting}

{name} — теперь доступна бесплатно 😲

Описание: [молодежный и понятный текст о том, почему это интересно]

🔗 [{link}]({link})

{signoff}

#бесплатныеигры #steamхалява #{game['id']}
        """
        return text.strip(), image_url, game['title']

    elif game and game['type'] == "epic":
        name = game['title']
        link = game['link']

        image_url = game.get('keyImages', [{}])[0].get('url', "")

        text = f"""
🎮 **{name}** — раздаётся бесплатно в Epic!

Не упусти шанс — просто авторизуйся и забери. Это отличный выбор, если любишь подобные проекты.

🔗 [{link}]({link})

{signoff}

#бесплатныеигры #epicхалява
        """
        return text.strip(), image_url, game['title']

    else:
        # Рандомная тема
        text = f"""
🔥 {topic}

[Это место может быть заполнено ИИ. Мы можем подключить Qwen API здесь.]

💡 Подробности внутри!
        """
        image_url = f"https://picsum.photos/seed/{random.randint(1, 999)}/600/400"
        return text.strip(), image_url, topic


async def send_poll(question, options):
    try:
        await bot.send_poll(
            chat_id=CHANNEL_USERNAME,
            question=question,
            options=options,
            type=PollType.REGULAR,
            is_anonymous=True
        )
        print("✅ Опрос опубликован!")
    except Exception as e:
        print(f"❌ Ошибка при отправке опроса: {e}")


async def send_post(text, image_url=None):
    try:
        if image_url:
            await bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=image_url,
                caption=text[:1024],
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
        print("✅ Пост успешно опубликован!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")


# =================== ЗАПУСК ==================== #

async def main():
    posts_published = load_published()
    post_ids = set(p["id"] for p in posts_published)

    post_type = random.choice(["steam", "epic", "topic"])

    if post_type == "steam":
        game = get_steam_free_game()
        if game and game["title"] not in post_ids:
            post_text, image_url, post_id = generate_post(game=game)
            await send_post(post_text, image_url)
            save_published(post_id)

    elif post_type == "epic":
        game = get_epic_free_game()
        if game and game["title"] not in post_ids:
            post_text, image_url, post_id = generate_post(game=game)
            await send_post(post_text, image_url)
            save_published(post_id)

    else:
        topic = random.choice(POST_TOPICS)
        if topic not in post_ids:
            post_text, image_url, post_id = generate_post(topic=topic)
            await send_post(post_text, image_url)
            save_published(post_id)

    # Иногда добавляем опрос
    if random.random() < 0.2:
        question, options = random.choice(POLL_QUESTIONS)
        await send_poll(question, options)


if __name__ == "__main__":
    asyncio.run(main())
