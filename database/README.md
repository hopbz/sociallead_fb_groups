# Database schema

Docker Compose tự mount `database/init.sql` vào PostgreSQL để tạo các bảng cần thiết:

- `group_sources`: danh sách Facebook Groups.
- `keywords`: keyword filter.
- `scraped_posts`: bài viết đã scrape.
- `scan_runs`: lịch sử lần quét.
- `error_logs`: lỗi theo từng group.
- `app_settings`: cấu hình nhỏ.

Backend cũng có `create_all()` bằng SQLAlchemy, nên khi chạy SQLite local vẫn tự tạo bảng.
