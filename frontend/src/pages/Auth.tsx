import { useState } from 'react';
import { KeyRound, Radio, ShieldCheck } from 'lucide-react';
import { api, getApiBaseUrl, getApiToken, saveApiConnection } from '../lib/api';

type Props = { onLogin: () => void };

export function Auth({ onLogin }: Props) {
  const [baseUrl, setBaseUrl] = useState(getApiBaseUrl());
  const [token, setToken] = useState(getApiToken());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function connect() {
    setBusy(true);
    setError('');
    try {
      saveApiConnection(baseUrl, token);
      await api.dashboard();
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#EBF1ED] grid place-items-center p-5">
      <div className="w-full max-w-5xl grid lg:grid-cols-[1.1fr_.9fr] gap-5">
        <section className="bg-slate-950 text-white rounded-[2rem] p-8 md:p-10 shadow-xl overflow-hidden relative">
          <div className="absolute -right-20 -top-20 h-64 w-64 bg-[#0866FF]/30 blur-3xl rounded-full" />
          <div className="relative">
            <div className="h-14 w-14 rounded-2xl bg-[#0866FF] grid place-items-center mb-6"><Radio size={28}/></div>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight leading-tight">SocialLead OS<br/><span className="text-[#60A5FA]">Facebook Groups SaaS</span></h1>
            <p className="text-slate-300 mt-5 leading-7 max-w-xl">Bản SaaS nhỏ đã được tinh gọn: chỉ quản lý group, keyword, chạy scraper, xem posts, run history, error logs, Telegram và Google Sheets.</p>
            <div className="grid md:grid-cols-3 gap-3 mt-8">
              {['Playwright engine', 'SeleniumBase fallback', 'PostgreSQL ready'].map(item => <div key={item} className="rounded-2xl bg-white/10 border border-white/10 p-4 font-bold text-sm">{item}</div>)}
            </div>
          </div>
        </section>
        <section className="bg-white rounded-[2rem] p-7 md:p-8 border border-slate-200 shadow-sm">
          <div className="h-12 w-12 rounded-2xl bg-blue-50 text-[#0866FF] grid place-items-center mb-4"><KeyRound/></div>
          <h2 className="text-2xl font-black">Kết nối backend</h2>
          <p className="text-sm text-slate-500 mt-2 leading-6">Nhập URL backend và API token trong file <b>.env</b>. Token được lưu local trong trình duyệt, không cần hard-code vào bundle frontend.</p>
          <div className="space-y-4 mt-6">
            <div>
              <label className="text-sm font-black">Backend URL</label>
              <input className="input mt-1" value={baseUrl} onChange={e=>setBaseUrl(e.target.value)} placeholder="http://localhost:3001" />
            </div>
            <div>
              <label className="text-sm font-black">API Token</label>
              <input className="input mt-1" value={token} onChange={e=>setToken(e.target.value)} placeholder="API_TOKEN trong .env" type="password" onKeyDown={e=>{ if(e.key==='Enter') void connect(); }} />
            </div>
            {error && <div className="rounded-2xl bg-red-50 border border-red-200 text-red-700 p-3 text-sm font-semibold whitespace-pre-wrap">{error}</div>}
            <button className="btn-primary w-full" onClick={connect} disabled={busy || !baseUrl}>{busy ? 'Đang kiểm tra...' : 'Vào dashboard'}</button>
          </div>
          <div className="rounded-2xl bg-green-50 text-green-700 p-4 mt-6 text-sm leading-6 flex gap-3"><ShieldCheck className="shrink-0"/> Chỉ dùng session trình duyệt đã đăng nhập thủ công. Không bypass CAPTCHA/checkpoint, không spam, không truy cập group không có quyền.</div>
        </section>
      </div>
    </div>
  );
}
