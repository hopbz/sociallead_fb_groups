from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import Settings
from app.core.scanner import FacebookGroupScanner
from app.db.session import SessionLocal
from app.schemas import ScanRequest

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_scheduler(settings: Settings) -> None:
    global _scheduler
    if not settings.scheduler_enabled:
        return
    if _scheduler and _scheduler.running:
        return

    def job() -> None:
        logger.info('Scheduler scan job started')
        with SessionLocal() as db:
            scanner = FacebookGroupScanner(settings, db)
            try:
                if (
                    settings.default_engine in ('playwright', 'cdp_playwright')
                    and not scanner.login_status(settings.default_engine).get('logged_in')
                ):
                    logger.info(
                        'Scheduler scan skipped because Facebook %s profile is not logged in',
                        settings.default_engine,
                    )
                    return
                scanner.scan(ScanRequest(engine=settings.default_engine))
            except Exception:
                logger.exception('Scheduler scan job failed')

    _scheduler = BackgroundScheduler(timezone='Asia/Bangkok')
    _scheduler.add_job(
        job,
        'interval',
        minutes=settings.scheduler_interval_minutes,
        id='facebook_group_scan',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )
    _scheduler.start()
    logger.info('Scheduler enabled interval=%s minutes', settings.scheduler_interval_minutes)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info('Scheduler stopped')
