import os
import re
import logging
import subprocess
import sys
import asyncio
import tempfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─── إعداد اللوق ────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── التوكن من متغير البيئة ──────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ─── أنماط الروابط المدعومة ──────────────────────────────────────────────────
SUPPORTED_PATTERNS = {
    "TikTok": re.compile(
        r"https?://(www\.)?(vm\.tiktok\.com|vt\.tiktok\.com|tiktok\.com)/[^\s]+"
    ),
    "Instagram": re.compile(
        r"https?://(www\.)?instagram\.com/(p|reel|tv|stories)/[^\s]+"
    ),
}

# أيقونات المنصات
PLATFORM_ICONS = {
    "TikTok": "🎵",
    "Instagram": "📸",
}


def detect_platform(url: str) -> str | None:
    """يكتشف المنصة من الرابط ويُعيد اسمها أو None."""
    for platform, pattern in SUPPORTED_PATTERNS.items():
        if pattern.search(url):
            return platform
    return None


def auto_update_ytdlp() -> None:
    """تحديث yt-dlp تلقائياً عند بدء التشغيل."""
    try:
        logger.info("جاري تحديث yt-dlp...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
            capture_output=True,
            text=True,
        )
        logger.info(result.stdout.strip() or "yt-dlp محدّث بالفعل")
    except Exception as e:
        logger.warning(f"تعذّر تحديث yt-dlp: {e}")


def download_video(url: str, platform: str) -> str | None:
    """
    تحميل الفيديو من أي منصة مدعومة باستخدام yt-dlp.
    يُعيد مسار الملف المحمّل أو None عند الفشل.
    """
    tmp_dir = tempfile.mkdtemp()
    output_template = os.path.join(tmp_dir, "%(id)s.%(ext)s")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-warnings",
        "--quiet",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-o", output_template,
    ]

    # إعدادات خاصة بانستقرام
    if platform == "Instagram":
        cmd += ["--add-header", "User-Agent:Mozilla/5.0"]

    cmd.append(url)

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp error [{platform}]: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        logger.error("انتهت مهلة التحميل")
        return None

    # البحث عن الملف المحمّل
    for f in os.listdir(tmp_dir):
        full_path = os.path.join(tmp_dir, f)
        if os.path.isfile(full_path):
            return full_path

    return None


# ─── معالجات البوت ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 أهلاً! أرسل لي رابط فيديو وسأحمّله لك بدون علامة مائية 🎬\n\n"
        "المنصات المدعومة:\n"
        "🎵 TikTok\n"
        "📸 Instagram (Reels, Posts, Stories)\n\n"
        "فقط أرسل الرابط مباشرة!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📌 *طريقة الاستخدام:*\n\n"
        "1. انسخ رابط الفيديو من التطبيق\n"
        "2. أرسله هنا مباشرة\n"
        "3. انتظر ثوانٍ وستصلك الفيديو ✅\n\n"
        "*المنصات المدعومة:*\n"
        "🎵 TikTok — بدون علامة مائية\n"
        "📸 Instagram — Reels & Posts & Stories",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""

    # استخراج أول رابط في الرسالة
    url_match = re.search(r"https?://[^\s]+", text)
    if not url_match:
        await update.message.reply_text(
            "⚠️ لم أجد رابطاً صحيحاً في رسالتك.\n\n"
            "أرسل رابطاً من:\n"
            "🎵 TikTok\n"
            "📸 Instagram"
        )
        return

    url = url_match.group(0)
    platform = detect_platform(url)

    if platform is None:
        await update.message.reply_text(
            "⚠️ هذا الرابط غير مدعوم حالياً.\n\n"
            "المنصات المدعومة:\n"
            "🎵 TikTok\n"
            "📸 Instagram"
        )
        return

    icon = PLATFORM_ICONS[platform]
    processing_msg = await update.message.reply_text(
        f"{icon} جاري تحميل الفيديو من {platform}، انتظر لحظة..."
    )

    # التحميل في thread منفصل لعدم تجميد البوت
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, download_video, url, platform)

    if file_path is None:
        await processing_msg.edit_text(
            f"❌ فشل التحميل من {platform}.\n"
            "تأكد من:\n"
            "• صحة الرابط\n"
            "• أن الحساب غير خاص (Private)\n"
            "ثم حاول مرة أخرى."
        )
        return

    file_size = os.path.getsize(file_path)
    # حد تيليغرام 50 ميغابايت للبوتات
    if file_size > 50 * 1024 * 1024:
        await processing_msg.edit_text(
            "⚠️ حجم الفيديو أكبر من 50 ميغابايت، لا يمكن إرساله عبر تيليغرام."
        )
        os.remove(file_path)
        return

    try:
        await processing_msg.edit_text("📤 جاري الإرسال...")
        with open(file_path, "rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f"✅ تم التحميل من {platform} {icon}\n🤖 @dirtiktok_bot",
                supports_streaming=True,
            )
        await processing_msg.delete()
    except Exception as e:
        logger.error(f"خطأ في الإرسال: {e}")
        await processing_msg.edit_text("❌ حدث خطأ أثناء إرسال الفيديو.")
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass


# ─── نقطة البداية ───────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN غير موجود في متغيرات البيئة!")
        sys.exit(1)

    # تحديث yt-dlp عند كل تشغيل
    auto_update_ytdlp()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("البوت يعمل الآن ✅ — يدعم TikTok و Instagram")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
