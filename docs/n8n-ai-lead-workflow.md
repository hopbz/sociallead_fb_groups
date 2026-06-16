# n8n AI Lead Qualification Workflow

File import: `n8n/workflows/ai_lead_workflow.json`

## Safety boundary

- The workflow never posts comments to Facebook.
- AI only drafts a suggested comment for human review.
- Do not bypass CAPTCHA or Facebook checkpoints.
- Use only groups the signed-in account is allowed to view.
- Start with conservative scan limits and a 30–60 minute schedule.

## Required environment variables

Configure these on the n8n host:

```env
BACKEND_BASE_URL=http://host.docker.internal:3001
BACKEND_API_TOKEN=replace-with-the-backend-api-token
TELEGRAM_CHAT_ID=replace-with-the-target-chat-id
AI_API_KEY=replace-with-your-ai-provider-key
```

`AI_API_KEY` is used when creating the OpenAI credential in n8n. The exported
workflow intentionally contains no credential IDs or real secrets.

If n8n runs outside Docker, use `http://localhost:3001` for
`BACKEND_BASE_URL`. If n8n and the backend share a Docker network, use the
backend service name, for example `http://backend:3001`.

## Import and credentials

1. Import `n8n/workflows/ai_lead_workflow.json`.
2. Open **OpenAI Chat Model**, create/select a credential using `AI_API_KEY`.
3. Open **Notify Telegram**, create/select a Telegram bot credential.
4. Confirm `TELEGRAM_CHAT_ID` points to the intended private chat or channel.
5. Keep the workflow inactive and run **Manual Trigger** once.
6. Inspect every node output before activating the schedule.

## Workflow

1. **Every 30 Minutes** or **Manual Trigger** starts the run.
2. **Scan Groups** calls `POST /api/v1/scan-groups` with 2 scrolls and 10 posts.
3. **Get Lead Scoring Settings** loads the current niche, tone, keyword lists,
   `score_threshold`, and safe scan settings.
4. **Get Unprocessed Posts** calls
   `GET /api/v1/posts/unprocessed?limit=50`.
5. **Normalize Posts** prepares one compact payload per post.
6. **Loop Over Posts** processes one post at a time.
7. **Lead Qualification Agent** returns strict JSON:

```json
{
  "score": 8,
  "need_stage": "hot",
  "persona": "Chủ salon đang tìm nhà cung cấp",
  "pain_points": ["cần báo giá", "cần triển khai sớm"],
  "reason": "Bài viết thể hiện nhu cầu mua rõ ràng.",
  "suggested_comment": "Bạn đang ưu tiên tiêu chí nào khi chọn nhà cung cấp?",
  "do_not_contact": false
}
```

8. **Score >= 7** compares the score with the configured
   `score_threshold` and requires `do_not_contact=false`.
9. Qualified leads are saved through `POST /api/v1/leads`, then sent to
   Telegram.
10. Both qualified and rejected posts call
    `PATCH /api/v1/posts/{post_id}/processed`.

## Telegram template

```text
🔥 Lead mới từ Facebook Group

📌 Group: {{group_name}}
👤 Tác giả: {{author}}
⭐ Score: {{score}}/10
🎯 Stage: {{need_stage}}

🧠 Lý do:
{{reason}}

💬 Comment đề xuất:
{{suggested_comment}}

🔗 Link bài viết:
{{post_url}}
```

## Reusing for different niches

Open **Cấu hình → Lead qualification** in SocialLead OS and change:

- `niche_name`
- `score_threshold`
- positive and negative keywords
- comment tone
- posts per group
- scan interval

Examples include salons, real estate, study abroad consulting, and agencies.
The n8n prompt reads these settings on every run.

## Troubleshooting

- `401`: verify `BACKEND_API_TOKEN` matches backend `API_TOKEN`.
- Connection refused: verify `BACKEND_BASE_URL` from inside the n8n runtime.
- Empty post list: run a scan and confirm posts have `processed_at = null`.
- AI JSON parse error: use a model that follows JSON instructions reliably.
- Telegram error: verify bot credential, chat ID, and bot membership.
