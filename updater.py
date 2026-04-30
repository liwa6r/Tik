"""
updater.py — يُشغَّل كـ cron job داخل Railway
يقوم بتحديث yt-dlp كل 24 ساعة تلقائياً ثم يعيد تشغيل البوت إذا لزم.
"""
import subprocess
import sys
import logging

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def update_ytdlp() -> bool:
    """يُحدّث yt-dlp ويُعيد True إذا صدر تحديث جديد."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    logger.info(output.strip())
    return "Successfully installed" in output


if __name__ == "__main__":
    updated = update_ytdlp()
    if updated:
        logger.info("✅ تم تحديث yt-dlp بنجاح")
    else:
        logger.info("ℹ️ yt-dlp محدّث بالفعل، لا يوجد جديد")
