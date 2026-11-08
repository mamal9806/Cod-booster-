# COD BOOSTER

[فارسی](#فارسی) · [English](#english)

## فارسی

**COD BOOSTER** یک پروژه اندرویدی با رابط کاربری الهام‌گرفته از Liquid Glass و یک موتور تحلیل‌گر محلی Python است. هدف پروژه کمک به بررسی وضعیت دستگاه و ارائه پیشنهادهای محتاطانه برای اجرای روان‌تر بازی Call of Duty: Mobile است.

### قابلیت‌های نسخه فعلی (0.2.0)
- رابط کاربری اندروید با Kotlin و Jetpack Compose
- اجرای موتور تحلیل Python داخل برنامه با Chaquopy
- بررسی اطلاعات قابل‌دسترسی دستگاه: RAM آزاد/کل، دمای باتری، وضعیت حرارتی سیستم و نوع اتصال شبکه
- تولید یافته‌ها و پیشنهادها به‌صورت محلی و بدون نیاز به سرویس ابری
- تست‌های واحد Python و گردش‌کار GitHub Actions برای اجرای آن‌ها

### محدودیت‌های مهم
- این موتور در حال حاضر **قاعده‌محور و توضیح‌پذیر** است؛ مدل یادگیری ماشین آموزش‌دیده یا LLM نیست.
- در این نسخه FPS واقعی بازی و ping واقعی سرورهای COD به برنامه متصل نشده‌اند؛ برنامه نباید این مقادیر را حدس بزند.
- بدون دسترسی روت، اندروید اجازه کنترل آزادانه فرکانس CPU/GPU یا بستن اجباری پردازش‌های سایر برنامه‌ها را به اپ معمولی نمی‌دهد.
- هیچ تضمینی برای افزایش FPS یا کاهش پینگ وجود ندارد. پیشنهادها باید ایمن، اختیاری و قابل بازگشت باشند.
- APK هنوز در CI یا روی دستگاه واقعی تأیید نشده است.

### ساخت پروژه
پروژه را با Android Studio و Gradle باز کنید. برای اجرای تست موتور Python:
```bash
python -m unittest discover -s ai_engine_tests -v
```

جزئیات ارتباط Kotlin و Python در فایل `PYTHON_ANDROID_BRIDGE.md` مستند شده است.

## English

**COD BOOSTER** is an Android project with a Liquid Glass-inspired interface and a local Python analysis engine. Its goal is to inspect available device signals and provide cautious recommendations that may help Call of Duty: Mobile run more smoothly.

### Current version (0.2.0)
- Android UI built with Kotlin and Jetpack Compose
- Embedded Python engine powered by Chaquopy
- Reads available device information: total/free RAM, battery temperature, Android thermal status, and network type
- Generates local findings and recommendations without a cloud service
- Python unit tests and a GitHub Actions workflow for running them

### Important limitations
- The current engine is **rule-based and explainable**; it is not a trained machine-learning model or an LLM.
- Actual in-game FPS and COD server ping are not integrated in this version. The app must not fabricate these values.
- Without root access, a regular Android app cannot freely control CPU/GPU frequencies or forcibly terminate other apps' processes.
- No FPS improvement or ping reduction is guaranteed. Recommendations should remain safe, optional, and reversible.
- The APK has not yet been verified by a CI Android build or on a physical device.

### Build
Open the project in Android Studio and let Gradle sync. To run the Python engine tests:
```bash
python -m unittest discover -s ai_engine_tests -v
```

See `PYTHON_ANDROID_BRIDGE.md` for details about the Kotlin-to-Python integration.

---
