# REMOVED FROM: backend/app/core/scheduler.py (Lines 75-82)
# This job was commented out and never used. Kept for reference.

# Job 2: Cleanup logs - Semanalmente domingos a las 3:00 AM
# scheduler.add_job(
#     cleanup_old_logs_job,
#     trigger=CronTrigger(day_of_week="sun", hour=3, minute=0, timezone="Asia/Tokyo"),
#     id="cleanup_logs",
#     name="Cleanup Old Logs (> 90 days)",
#     replace_existing=True,
# )

# The cleanup_old_logs_job function (lines 48-54) was also removed:
# async def cleanup_old_logs_job():
#     """
#     Job para limpieza de logs antiguos (> 90 días).
#     Puede implementarse en el futuro.
#     """
#     logger.info("🧹 Cleanup logs job - Not implemented yet")
#     pass
