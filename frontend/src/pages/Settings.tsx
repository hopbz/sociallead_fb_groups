import { useEffect, useState } from 'react';
import { Code2, LoaderCircle, Save, Send, Settings2 } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { ErrorBox, Loading } from '../components/State';

export function Settings() {
  const { data, loading, error, reload } = useAsync(api.settings, []);
  const {
    data: telegram,
    loading: telegramLoading,
    error: telegramError,
    reload: reloadTelegram,
  } = useAsync(api.telegramSettings, []);
  const [telegramEnabled, setTelegramEnabled] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState('');
  const [telegramBusy, setTelegramBusy] = useState(false);
  const [telegramNotice, setTelegramNotice] = useState('');
  const [telegramFormError, setTelegramFormError] = useState('');

  useEffect(() => {
    if (!telegram) return;
    setTelegramEnabled(telegram.enabled);
    setTelegramChatId(telegram.chat_id);
  }, [telegram]);

  async function saveTelegram() {
    setTelegramBusy(true);
    setTelegramNotice('');
    setTelegramFormError('');
    try {
      await api.saveTelegramSettings({ enabled: telegramEnabled, chat_id: telegramChatId.trim() });
      setTelegramNotice('Đã lưu cấu hình Telegram.');
      await Promise.all([reloadTelegram(), reload()]);
    } catch (err) {
      setTelegramFormError(err instanceof Error ? err.message : String(err));
    } finally {
      setTelegramBusy(false);
    }
  }

  async function testTelegram() {
    setTelegramBusy(true);
    setTelegramNotice('');
    setTelegramFormError('');
    try {
      await api.saveTelegramSettings({ enabled: telegramEnabled, chat_id: telegramChatId.trim() });
      const result = await api.testTelegram();
      setTelegramNotice(result.message);
      await reloadTelegram();
    } catch (err) {
      setTelegramFormError(err instanceof Error ? err.message : String(err));
    } finally {
      setTelegramBusy(false);
    }
  }

  return (
    <div>
      <Topbar
        title="Cấu hình hệ thống"
        subtitle="Quản lý thông báo Telegram và các thông số runtime của backend."
        onRefresh={() => void Promise.all([reload(), reloadTelegram()])}
      />

      <section className="card-premium mb-5 p-5 md:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end">
          <div className="flex-1">
            <p className="eyebrow">Telegram notification</p>
            <h2 className="mt-2 text-xl font-semibold tracking-[-0.03em]">Gửi bài viết mới về Telegram</h2>
            <p className="mt-2 text-xs leading-5 text-[#7d8784]">
              Chat ID được lưu trong database. Bot token chỉ đọc từ biến môi trường và không được trả về frontend.
            </p>
            <label className="mt-5 block">
              <span className="mb-2 block text-xs font-semibold text-[#52605d]">Telegram chat ID</span>
              <input
                className="input"
                placeholder="Ví dụ: 8850401551 hoặc -100xxxxxxxxxx"
                value={telegramChatId}
                disabled={telegramLoading || telegramBusy}
                onChange={event => setTelegramChatId(event.target.value)}
              />
            </label>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className={`btn-soft ${telegramEnabled ? '!border-[#54a69e] !bg-[#eff9f6]' : ''}`}
              disabled={telegramLoading || telegramBusy}
              onClick={() => setTelegramEnabled(value => !value)}
            >
              {telegramEnabled ? 'Đang bật thông báo' : 'Đang tắt thông báo'}
            </button>
            <button className="btn-soft" disabled={telegramBusy || !telegramChatId.trim()} onClick={testTelegram}>
              {telegramBusy ? <LoaderCircle size={16} className="animate-spin" /> : <Send size={16} />}
              Gửi thử
            </button>
            <button className="btn-primary" disabled={telegramBusy} onClick={saveTelegram}>
              {telegramBusy ? <LoaderCircle size={16} className="animate-spin" /> : <Save size={16} />}
              Lưu
            </button>
          </div>
        </div>
        {telegram && (
          <p className="mt-4 text-xs text-[#66706d]">
            Bot token: <strong>{telegram.bot_token_configured ? 'Đã cấu hình' : 'Chưa cấu hình trong .env'}</strong>
          </p>
        )}
        {(telegramError || telegramFormError) && (
          <div className="mt-4"><ErrorBox message={telegramFormError || telegramError || ''} /></div>
        )}
        {telegramNotice && (
          <div className="mt-4 rounded-xl border border-[#b9ddd4] bg-[#eef9f6] p-3 text-xs font-semibold text-[#17685f]">
            {telegramNotice}
          </div>
        )}
      </section>

      {loading ? <Loading /> : error ? <ErrorBox message={error} /> : data && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Object.entries(data).map(([key, value], index) => (
            <div key={key} className="card-premium interactive-card row-reveal p-5" style={{ '--row-index': index } as React.CSSProperties}>
              <div className="flex items-center justify-between gap-4">
                <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#e1e8e6] text-[#16776f]"><Settings2 size={16} /></span>
                <span className={`badge ${value === true ? 'badge-success' : value === false ? 'badge-info' : 'badge-warning'}`}>{String(value)}</span>
              </div>
              <p className="mt-5 break-all text-xs font-semibold uppercase tracking-[0.08em] text-[#52605d]">{key.replace(/_/g, ' ')}</p>
            </div>
          ))}
        </div>
      )}

      <section className="mt-5 overflow-hidden rounded-[20px] bg-[#102b2a] text-white">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div><p className="text-sm font-semibold">n8n Endpoint</p><p className="mt-1 text-[11px] text-white/45">Mẫu tích hợp automation</p></div>
          <Code2 size={19} className="text-[#8fd0c4]" />
        </div>
        <pre className="overflow-auto p-5 text-xs leading-6 text-white/75">POST http://localhost:3001/api/v1/scan-groups{`\n`}Header: X-API-Token: API_TOKEN{`\n\n`}{`{
  "engine": "cdp_playwright",
  "max_scrolls": 8,
  "max_posts_per_group": 50,
  "send_telegram": true,
  "write_google_sheets": true
}`}</pre>
      </section>
    </div>
  );
}
