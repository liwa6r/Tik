# 🎬 TikTok Downloader Bot — @dirtiktok_bot

بوت تيليغرام لتحميل فيديوهات تيك توك بدون علامة مائية، مستضاف على Railway.

---

## 🚀 خطوات النشر على Railway

### 1. رفع المشروع على GitHub
1. أنشئ **Repository جديد** على [github.com](https://github.com)
2. ارفع جميع ملفات المشروع إليه

### 2. ربط Railway بـ GitHub
1. اذهب إلى [railway.app](https://railway.app) وسجّل الدخول
2. اضغط **New Project** ← **Deploy from GitHub repo**
3. اختر الـ Repository الذي رفعت إليه المشروع

### 3. إضافة متغير البيئة (مهم جداً)
في لوحة Railway:
1. اضغط على الـ Service
2. اذهب إلى تبويب **Variables**
3. أضف المتغير التالي:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | `ضع توكن البوت هنا` |

### 4. التشغيل
بعد إضافة المتغير، سيبدأ Railway بنشر البوت تلقائياً ✅

---

## 🔄 التحديث التلقائي

- **yt-dlp** يتحدث تلقائياً عند **كل إعادة تشغيل** للبوت
- Railway يُعيد تشغيل البوت تلقائياً عند أي خطأ (`ON_FAILURE`)
- عند رفع أي تحديث على GitHub، يُعيد Railway النشر تلقائياً

---

## 📁 هيكل المشروع

```
tiktok_bot/
├── bot.py           # الكود الرئيسي للبوت
├── updater.py       # سكريبت التحديث اليدوي
├── requirements.txt # المكتبات المطلوبة
├── Procfile         # أمر تشغيل Railway
├── railway.json     # إعدادات Railway
└── README.md        # هذا الملف
```

---

## ⚙️ المكتبات المستخدمة

| المكتبة | الوظيفة |
|---------|---------|
| `python-telegram-bot` | التواصل مع تيليغرام API |
| `yt-dlp` | تحميل الفيديوهات بدون علامة مائية |
