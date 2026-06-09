from app.config import get_settings
from app.core.scanner import FacebookGroupScanner
from app.db.session import SessionLocal, init_db
from app.schemas import ScanRequest

if __name__ == '__main__':
    init_db()
    with SessionLocal() as db:
        response = FacebookGroupScanner(get_settings(), db).scan(ScanRequest())
        print(response.model_dump_json(indent=2))
