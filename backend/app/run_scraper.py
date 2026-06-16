# backend/app/run_scraper.py
"""
Script CLI độc lập để chạy FacebookStealthScraper thủ công.
Chạy từ thư mục gốc dự án:
    python -m app.run_scraper
hoặc từ thư mục backend/:
    python -m app.run_scraper
"""
from __future__ import annotations

import json
import os
import sys

# Đảm bảo thư mục `backend/` nằm trong sys.path khi chạy trực tiếp
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.stealth_scraper import FacebookStealthScraper  # noqa: E402
from app.config import Config  # noqa: E402


def main() -> None:
    scraper = FacebookStealthScraper()
    try:
        scraper.init_driver(headless=False, use_cdp=True)
        print("🔐 Đang đăng nhập…")
        if not scraper.login_facebook(
            email=Config.FB_EMAIL or None,
            password=Config.FB_PASSWORD or None,
        ):
            print("❌ Đăng nhập thất bại.")
            return
        print("✅ Đã đăng nhập.")

        print("\n📋 Menu:")
        print("  1. Thu thập bài viết từ group")
        print("  2. Trích xuất SĐT từ profile")
        print("  3. Lấy danh sách member IDs")
        print("  4. Tự động đăng bài vào group")
        choice = input("Chọn (1-4): ").strip()

        if choice == "1":
            url = input("Group URL: ").strip()
            max_p = int(input("Số bài tối đa [50]: ").strip() or "50")
            posts = scraper.scrape_group_posts(url, max_p)
            out_file = "posts.json"
            with open(out_file, "w", encoding="utf-8") as fh:
                json.dump(posts, fh, indent=2, ensure_ascii=False)
            print(f"✅ Đã lưu {len(posts)} bài → {out_file}")

        elif choice == "2":
            url = input("Profile URL: ").strip()
            phone = scraper.extract_profile_phone(url)
            print(f"📞 SĐT: {phone if phone else 'Không tìm thấy'}")

        elif choice == "3":
            url = input("Group URL: ").strip()
            limit = int(input("Số thành viên tối đa [100]: ").strip() or "100")
            ids = scraper.extract_group_member_ids(url, limit)
            print(f"👥 Đã lấy {len(ids)} ID thành viên.")

        elif choice == "4":
            url = input("Group URL: ").strip()
            content = input("Nội dung bài đăng: ").strip()
            img = input("Đường dẫn ảnh (Enter để bỏ qua): ").strip()
            ok = scraper.auto_post_to_group(url, content, img or None)
            print("✅ Đã đăng." if ok else "❌ Đăng thất bại.")

        else:
            print("Lựa chọn không hợp lệ.")

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng.")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
