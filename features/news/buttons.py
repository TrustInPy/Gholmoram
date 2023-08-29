from telethon.sync import Button


news_keyboard = [
    [Button.inline("💬 اخبار برتر روز", "Day")],
    [
        Button.inline("🌐 اخبار سیاسی", "Politic"),
        Button.inline("⚽️ اخبار ورزشی", "Sport"),
    ],
    [
        Button.inline("📊 اخبار اقتصادی", "Economy"),
        Button.inline("🎬 اخبار فرهنگ و هنر", "Calture"),
    ],
    [Button.inline("⬅️ بازگشت", "Cancel")],
]
