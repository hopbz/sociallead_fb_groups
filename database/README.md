# Database schema

Docker Compose tự mount `database/init.sql` vào PostgreSQL để tạo các bảng cần thiết:

- `group_sources`: danh sách Facebook Groups.
- `keywords`: keyword filter.
- `scraped_posts`: bài viết đã scrape.
- `lead_candidates`: lead được AI qualification và chờ human review.
- `scan_runs`: lịch sử lần quét.
- `error_logs`: lỗi theo từng group.
- `app_settings`: cấu hình nhỏ.

Backend cũng có `create_all()` bằng SQLAlchemy, nên khi chạy SQLite local vẫn tự tạo bảng.

Migration bổ sung lead workflow cho PostgreSQL:

```bash
psql "$DATABASE_URL" -f database/migrations/20260612_add_lead_automation.sql
```

Backup database trước khi chạy migration trên môi trường có dữ liệu thật.
