from app.db.session import SessionLocal, init_db
from app.db.models import GroupSource, Keyword

EXAMPLE_GROUPS = [
    ("Example Facebook Group", "https://www.facebook.com/groups/your_group_slug"),
]
EXAMPLE_KEYWORDS = ["java", "spring boot", "thực tập", "tuyển dụng"]

if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        for name, url in EXAMPLE_GROUPS:
            exists = db.query(GroupSource).filter(GroupSource.url == url).first()
            if not exists:
                db.add(GroupSource(name=name, url=url, is_active=True))
        for kw in EXAMPLE_KEYWORDS:
            exists = db.query(Keyword).filter(Keyword.keyword == kw).first()
            if not exists:
                db.add(Keyword(keyword=kw, is_active=True))
        db.commit()
    print("Seed demo data completed. Replace example group URL in the UI before scanning.")
