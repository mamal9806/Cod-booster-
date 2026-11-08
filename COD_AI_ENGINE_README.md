# COD AI ENGINE (Python)

موتور تحلیل و پیشنهاد بهینه‌سازی COD BOOSTER. این نسخه هسته‌ی Python مستقل و قابل‌تست است.

## قابلیت‌ها
- تحلیل RAM آزاد، دمای باتری، وضعیت حرارتی اندروید، پینگ، جیتر، Packet Loss و FPS در صورت وجود داده معتبر
- تشخیص گلوگاه‌های احتمالی و سطح اطمینان
- ساخت پیشنهادهای مرحله‌ای با توضیح، ریسک و اثر احتمالی
- اجرای self-test داخلی
- بدون وابستگی خارجی؛ فقط Python Standard Library

## اجرا
```bash
python cod_booster_ai.py
```
یا:
```python
from cod_booster_ai import analyze_device, self_test
print(self_test())
report = analyze_device(
    {
      "ram_total_mb": 8192,
      "ram_available_mb": 2100,
      "battery_temp_c": 37.5,
      "thermal_status": "light",
      "ping_ms": 48,
      "jitter_ms": 9,
      "packet_loss_percent": 0,
      "game_fps_avg": 55,
      "game_fps_min": 42
    },
    {"target_fps": 60, "graphics_preference": "fps"}
)
print(report)
```

## قرارداد داده
مقادیر باید از APIهای مجاز اندروید یا ابزار معتبر اندازه‌گیری بیایند. اگر داده‌ای موجود نیست، آن را حذف کنید؛ مقدار ساختگی صفر ندهید. FPS و frame time را فقط از منبع قابل‌اعتماد وارد کنید.

## ایمنی و محدودیت
این موتور تحلیل و پیشنهاد تولید می‌کند و خودش تنظیمات سیستم‌عامل یا بازی را تغییر نمی‌دهد. اپ عادی اندروید بدون روت اجازه‌ی کشتن آزادانه‌ی برنامه‌های دیگر، اجبار فرکانس CPU/GPU یا دستکاری فایل‌های COD را ندارد. هر تغییر باید به‌صورت پیشنهاد شفاف به کاربر نمایش داده شود و فقط از مسیرهای مجاز و با تأیید کاربر انجام شود.

## English
An explainable, deterministic Python optimization planner. It analyzes available device/network/game metrics, emits confidence-scored findings and safe recommendations, and includes a built-in smoke-test suite. It does not autonomously alter Android or game settings. Missing telemetry is treated as unknown, not as a healthy zero.
