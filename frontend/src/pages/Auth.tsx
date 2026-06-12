import { useState } from 'react';
import { CheckCircle2, KeyRound, Radio, ShieldCheck } from 'lucide-react';
import { motion } from 'motion/react';
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
    <div className="app-canvas grid min-h-screen place-items-center p-4 md:p-7">
      <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .5, ease: [0.22, 1, 0.36, 1] }} className="grid w-full max-w-6xl overflow-hidden rounded-[28px] border border-[#dfe3dc] bg-white shadow-[0_30px_90px_rgba(16,43,42,.14)] lg:grid-cols-[1.08fr_.92fr]">
        <section className="relative overflow-hidden bg-[#102b2a] p-8 text-white md:p-12">
          <div className="absolute inset-0 opacity-40" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px)', backgroundSize: '40px 40px' }} />
          <div className="absolute -right-16 -top-20 h-72 w-72 rounded-full bg-[#16776f]/55 blur-[95px]" />
          <div className="relative flex h-full flex-col">
            <span className="grid h-12 w-12 place-items-center rounded-xl bg-[#d9eee9] text-[#102b2a]"><Radio size={23} /></span>
            <p className="mt-10 text-[11px] font-bold uppercase tracking-[0.18em] text-[#8fd0c4]">Facebook intelligence workspace</p>
            <h1 className="mt-4 max-w-xl text-4xl font-medium leading-[1.08] tracking-[-0.055em] md:text-5xl">Biến tín hiệu cộng đồng thành dữ liệu có thể hành động.</h1>
            <p className="mt-5 max-w-xl text-sm leading-7 text-white/52">Quản lý nguồn group, keyword, phiên quét và bài viết trong một trung tâm vận hành tập trung.</p>
            <div className="mt-10 grid gap-3 sm:grid-cols-3">
              {['Playwright engine', 'Keyword intelligence', 'PostgreSQL ready'].map(item => <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4 text-xs font-semibold text-white/72"><CheckCircle2 className="mb-4 text-[#8fd0c4]" size={17} />{item}</div>)}
            </div>
            <p className="mt-auto pt-10 text-[10px] text-white/30">SocialLead OS · Local-first operations</p>
          </div>
        </section>

        <section className="p-7 md:p-10 lg:p-12">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-[#d9eee9] text-[#16776f]"><KeyRound size={20} /></span>
          <p className="eyebrow mt-7">Secure connection</p>
          <h2 className="mt-2 text-3xl font-semibold tracking-[-0.045em]">Kết nối backend</h2>
          <p className="mt-3 text-sm leading-6 text-[#66706d]">Nhập địa chỉ API và token trong file môi trường. Thông tin chỉ được lưu cục bộ trong trình duyệt.</p>
          <div className="mt-7 space-y-5">
            <label className="block"><span className="mb-2 block text-xs font-semibold text-[#52605d]">Backend URL</span><input className="input" value={baseUrl} onChange={event => setBaseUrl(event.target.value)} placeholder="http://localhost:3001" /></label>
            <label className="block"><span className="mb-2 block text-xs font-semibold text-[#52605d]">API Token</span><input className="input" value={token} onChange={event => setToken(event.target.value)} placeholder="API_TOKEN trong .env" type="password" onKeyDown={event => { if (event.key === 'Enter') void connect(); }} /></label>
            {error && <div className="rounded-xl border border-[#efc7c2] bg-[#fff4f2] p-3 text-xs font-semibold text-[#a33f38]">{error}</div>}
            <button className="btn-primary min-h-12 w-full" onClick={connect} disabled={busy || !baseUrl}>{busy ? 'Đang xác minh kết nối...' : 'Vào workspace'}</button>
          </div>
          <div className="mt-7 flex gap-3 rounded-2xl bg-[#f7f8f5] p-4 text-xs leading-5 text-[#66706d]"><ShieldCheck className="shrink-0 text-[#16776f]" size={19} />Chỉ sử dụng session đã đăng nhập thủ công; không vượt CAPTCHA, checkpoint hoặc quyền truy cập.</div>
        </section>
      </motion.div>
    </div>
  );
}
