# Hybrid AI Chatbot Core

هسته مستقل چت‌بات ترکیبی Python. از هر سرویس دارای API سازگار با OpenAI Chat Completions پشتیبانی می‌کند؛ از جمله سرویس‌های میزبانی‌شده و gateway محلی Ollama.

## قابلیت‌ها
- اتصال قابل‌تعویض به مدل زبانی آنلاین یا endpoint محلی
- تاریخچه پایدار جداگانه برای هر گفت‌وگو
- محدودیت طول context و تاریخچه
- fallback آفلاین شفاف هنگام نبود مدل یا قطع ارتباط
- حذف تاریخچه گفت‌وگو
- فقط Python Standard Library؛ بدون وابستگی خارجی
- کلید API فقط از متغیر محیطی خوانده می‌شود

## راه‌اندازی
نمونه استفاده:
    from hybrid_chatbot import HybridChatbot
    bot = HybridChatbot.from_env(memory_dir="./data/chat-history")
    result = bot.chat("main", "سلام! خودت رو معرفی کن")
    print(result["answer"], result["mode"])

متغیرهای محیطی:
- AI_BASE_URL: آدرس پایه endpoint؛ برای نمونه آدرس API ارائه‌دهنده یا http://localhost:11434/v1 برای endpoint سازگار Ollama
- AI_MODEL: شناسه مدل
- AI_API_KEY: کلید API؛ ممکن است برای سرور محلی لازم نباشد

## تست
    PYTHONPATH=ai_chatbot python -m unittest discover -s ai_chatbot/tests -v

## محدودیت‌ها و امنیت
- fallback آفلاین فعلی فقط پاسخ‌های پایه و شفاف دارد؛ خودش LLM آفلاین نیست.
- برای اجرای LLM واقعی بدون اینترنت باید مدل محلی متناسب با RAM و فضای دستگاه نصب شود.
- تاریخچه فعلاً JSON محلی است؛ رمزنگاری و سیاست نگهداری داده باید پیش از انتشار عمومی اضافه شوند.
- هرگز کلید API را در Git یا سورس قرار ندهید.
