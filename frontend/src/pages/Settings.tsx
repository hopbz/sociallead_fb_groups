import { useEffect, useState } from 'react';
import { Code2, KeyRound, LoaderCircle, Save, Send, Settings2, SlidersHorizontal } from 'lucide-react';
import { api } from '../lib/api';
import type { LeadScoringSettings } from '../lib/api';
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
  const [telegramBotToken, setTelegramBotToken] = useState('');
  const [telegramBusy, setTelegramBusy] = useState(false);
  const [telegramNotice, setTelegramNotice] = useState('');
  const [telegramFormError, setTelegramFormError] = useState('');
  const {
    data: leadScoring,
    loading: scoringLoading,
    error: scoringError,
    reload: reloadScoring,
  } = useAsync(api.leadScoringSettings, []);
  const [scoringForm, setScoringForm] = useState<LeadScoringSettings | null>(null);
  const [scoringBusy, setScoringBusy] = useState(false);
  const [scoringNotice, setScoringNotice] = useState('');
  const [scoringFormError, setScoringFormError] = useState('');

  useEffect(() => {
    if (!telegram) return;
    setTelegramEnabled(telegram.enabled);
    setTelegramChatId(telegram.chat_id);
    setTelegramBotToken('');
  }, [telegram]);

  useEffect(() => {
    if (leadScoring) setScoringForm(leadScoring);
  }, [leadScoring]);

  async function saveTelegram() {
    setTelegramBusy(true);
    setTelegramNotice('');
    setTelegramFormError('');
    try {
      await api.saveTelegramSettings(buildTelegramPayload());
      setTelegramBotToken('');
      setTelegramNotice('Đã lưu cấu hình Telegram vào backend và .env.');
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
      await api.saveTelegramSettings(buildTelegramPayload());
      const result = await api.testTelegram();
      setTelegramBotToken('');
      setTelegramNotice(result.message);
      await reloadTelegram();
    } catch (err) {
      setTelegramFormError(err instanceof Error ? err.message : String(err));
    } finally {
      setTelegramBusy(false);
    }
  }

  async function saveScoring() {
    if (!scoringForm) return;
    setScoringBusy(true);
    setScoringNotice('');
    setScoringFormError('');
    try {
      await api.saveLeadScoringSettings(scoringForm);
      setScoringNotice('Đã lưu cấu hình chấm điểm lead vào backend và .env.');
      await reloadScoring();
    } catch (err) {
      setScoringFormError(err instanceof Error ? err.message : String(err));
    } finally {
      setScoringBusy(false);
    }
  }

  function updateScoring<K extends keyof LeadScoringSettings>(key: K, value: LeadScoringSettings[K]) {
    setScoringForm(current => current ? { ...current, [key]: value } : current);
  }

  function buildTelegramPayload() {
    const payload: { enabled: boolean; chat_id: string; bot_token?: string } = {
      enabled: telegramEnabled,
      chat_id: telegramChatId.trim(),
    };
    const token = telegramBotToken.trim();
    if (token) payload.bot_token = token;
    return payload;
  }

  function parseKeywords(value: string) {
    return value.split(',').map(item => item.trim()).filter(Boolean);
  }

  return (
    <div>
      <Topbar
        title="Cấu hình hệ thống"
        subtitle="Quản lý thông báo Telegram và các thông số runtime của backend."
        onRefresh={() => void Promise.all([reload(), reloadTelegram(), reloadScoring()])}
      />

      <section className="card-premium mb-5 p-5 md:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end">
          <div className="flex-1">
            <p className="eyebrow">Telegram notification</p>
            <h2 className="mt-2 text-xl font-semibold tracking-[-0.03em]">Gửi bài viết mới về Telegram</h2>
            <p className="mt-2 text-xs leading-5 text-[#7d8784]">
              Chat ID và bot token được backend lưu vào file .env. Token hiện tại không được trả về frontend.
            </p>
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <label className="block">
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Telegram chat ID</span>
                <input
                  className="input"
                  placeholder="Ví dụ: 8850401551 hoặc -100xxxxxxxxxx"
                  value={telegramChatId}
                  disabled={telegramLoading || telegramBusy}
                  onChange={event => setTelegramChatId(event.target.value)}
                />
              </label>
              <label className="block">
                <span className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-[#52605d]">
                  <KeyRound size={14} />
                  Bot token
                </span>
                <input
                  className="input"
                  type="password"
                  autoComplete="off"
                  placeholder={telegram?.bot_token_configured ? 'Nhập token mới nếu muốn cập nhật' : 'Nhập bot token Telegram'}
                  value={telegramBotToken}
                  disabled={telegramLoading || telegramBusy}
                  onChange={event => setTelegramBotToken(event.target.value)}
                />
              </label>
            </div>
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

      <section className="card-premium mb-5 p-5 md:p-6">
        <div className="flex items-start gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#d9eee9] text-[#16776f]">
            <SlidersHorizontal size={18} />
          </span>
          <div>
            <p className="eyebrow">Lead qualification</p>
            <h2 className="mt-2 text-xl font-semibold tracking-[-0.03em]">Cấu hình chấm điểm theo ngành</h2>
            <p className="mt-2 text-xs leading-5 text-[#7d8784]">
              Các giá trị này được n8n dùng để điều chỉnh prompt, ngưỡng lưu lead và nhịp quét an toàn.
            </p>
          </div>
        </div>

        {scoringLoading ? <div className="mt-5"><Loading /></div> : (scoringError || scoringFormError) ? (
          <div className="mt-5"><ErrorBox message={scoringFormError || scoringError || ''} /></div>
        ) : scoringForm && (
          <>
            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <label>
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Ngành / niche</span>
                <input className="input" value={scoringForm.niche_name} onChange={event => updateScoring('niche_name', event.target.value)} />
              </label>
              <label>
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Score threshold</span>
                <input className="input" type="number" min={1} max={10} value={scoringForm.score_threshold} onChange={event => updateScoring('score_threshold', Number(event.target.value))} />
              </label>
              <label>
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Post mỗi group</span>
                <input className="input" type="number" min={1} max={100} value={scoringForm.max_posts_per_group} onChange={event => updateScoring('max_posts_per_group', Number(event.target.value))} />
              </label>
              <label>
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Chu kỳ quét (phút)</span>
                <input className="input" type="number" min={15} max={1440} value={scoringForm.scan_interval_minutes} onChange={event => updateScoring('scan_interval_minutes', Number(event.target.value))} />
              </label>
              <label className="md:col-span-2">
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Từ khóa tích cực, cách nhau bằng dấu phẩy</span>
                <input className="input" value={scoringForm.positive_keywords.join(', ')} onChange={event => updateScoring('positive_keywords', parseKeywords(event.target.value))} />
              </label>
              <label className="md:col-span-2 lg:col-span-3">
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Từ khóa loại trừ</span>
                <input className="input" value={scoringForm.negative_keywords.join(', ')} onChange={event => updateScoring('negative_keywords', parseKeywords(event.target.value))} />
              </label>
              <label className="md:col-span-2 lg:col-span-3">
                <span className="mb-2 block text-xs font-semibold text-[#52605d]">Tone comment đề xuất</span>
                <textarea className="input min-h-24 resize-y" value={scoringForm.comment_tone} onChange={event => updateScoring('comment_tone', event.target.value)} />
              </label>
            </div>
            <div className="mt-4 flex items-center justify-between gap-3">
              <p className="text-xs text-[#7d8784]">AI chỉ soạn comment để người vận hành review, không tự đăng Facebook.</p>
              <button className="btn-primary shrink-0" disabled={scoringBusy} onClick={saveScoring}>
                {scoringBusy ? <LoaderCircle size={16} className="animate-spin" /> : <Save size={16} />}
                Lưu scoring
              </button>
            </div>
            {scoringNotice && <p className="mt-3 text-xs font-semibold text-[#16776f]">{scoringNotice}</p>}
          </>
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
