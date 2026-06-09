import { useState } from 'react';
import { LogIn, Play, ShieldCheck } from 'lucide-react';
import { api, type EngineName, type LoginStatus } from '../lib/api';
import { Topbar } from '../components/Topbar';
import { ErrorBox } from '../components/State';

export function Scanner() {
  const [engine, setEngine] = useState<EngineName>('cdp_playwright');
  const [maxScrolls, setMaxScrolls] = useState(8);
  const [maxPosts, setMaxPosts] = useState(50);
  const [sendTelegram, setSendTelegram] = useState(true);
  const [writeSheet, setWriteSheet] = useState(true);
  const [busy, setBusy] = useState(false);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginStatus, setLoginStatus] = useState<LoginStatus | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function checkLogin() {
    setError(null);
    try {
      setLoginStatus(await api.loginStatus(engine));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function login() {
    setLoginBusy(true);
    setError(null);
    try {
      setLoginStatus(await api.login(engine));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoginBusy(false);
    }
  }

  async function run() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.scan({
        engine,
        max_scrolls: maxScrolls,
        max_posts_per_group: maxPosts,
        send_telegram: sendTelegram,
        write_google_sheets: writeSheet,
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Topbar title="Run Scanner" subtitle="Chạy quét Facebook Groups theo cấu hình hiện tại." />

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="card-premium p-5 lg:col-span-2 space-y-4">
          <div>
            <label className="text-sm font-black">Engine</label>
            <select className="input mt-1" value={engine} onChange={e => setEngine(e.target.value as EngineName)}>
              <option value="cdp_playwright">CDP Playwright</option>
              <option value="playwright">Playwright</option>
              <option value="seleniumbase">SeleniumBase</option>
            </select>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-black">Max scrolls/group</label>
              <input className="input mt-1" type="number" value={maxScrolls} onChange={e => setMaxScrolls(Number(e.target.value))} />
            </div>
            <div>
              <label className="text-sm font-black">Max posts/group</label>
              <input className="input mt-1" type="number" value={maxPosts} onChange={e => setMaxPosts(Number(e.target.value))} />
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button className="btn-soft" onClick={checkLogin} disabled={loginBusy || busy}>Kiểm tra đăng nhập</button>
            <button className="btn-soft" onClick={login} disabled={loginBusy || busy}>
              <LogIn size={18} />
              {loginBusy ? 'Đang chờ đăng nhập...' : 'Mở Playwright đăng nhập'}
            </button>
            {loginStatus && (
              <span className={`badge ${loginStatus.logged_in ? 'badge-success' : 'badge-warning'}`}>
                {loginStatus.logged_in ? 'Đã đăng nhập' : 'Chưa đăng nhập'}
              </span>
            )}
          </div>

          <label className="flex items-center gap-3 font-bold">
            <input type="checkbox" checked={sendTelegram} onChange={e => setSendTelegram(e.target.checked)} />
            Gửi Telegram nếu bật trong .env
          </label>
          <label className="flex items-center gap-3 font-bold">
            <input type="checkbox" checked={writeSheet} onChange={e => setWriteSheet(e.target.checked)} />
            Ghi Google Sheets nếu bật trong .env
          </label>

          <button className="btn-primary w-full md:w-auto" onClick={run} disabled={busy}>
            <Play size={18} />
            {busy ? 'Đang quét...' : 'Chạy quét ngay'}
          </button>
        </div>

        <div className="card-premium p-5">
          <div className="h-12 w-12 bg-green-50 text-green-600 rounded-2xl grid place-items-center mb-3"><ShieldCheck /></div>
          <h3 className="font-black">Safe Mode</h3>
          <p className="text-sm text-slate-500 leading-6 mt-2">
            Hệ thống dùng session trình duyệt bạn đăng nhập thủ công, lưu profile/cookie để quét các group tài khoản đã có quyền xem.
          </p>
        </div>
      </div>

      {error && <div className="mt-5"><ErrorBox message={error} /></div>}
      {result && (
        <div className="card-premium p-5 mt-5">
          <h3 className="font-black mb-3">Kết quả</h3>
          <pre className="bg-slate-950 text-slate-50 rounded-2xl p-4 overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
