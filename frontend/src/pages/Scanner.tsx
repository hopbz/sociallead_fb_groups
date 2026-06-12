import { useState } from 'react';
import { motion } from 'motion/react';
import { Check, FolderLock, LoaderCircle, LogIn, Play, Radar, ShieldCheck } from 'lucide-react';
import { api, type EngineName, type LoginStatus, type ScanResponse } from '../lib/api';
import { useAsync } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { ErrorBox } from '../components/State';

const engineSafety: Record<EngineName, {
  eyebrow: string;
  title: string;
  description: string;
  details: string[];
  profile: string;
}> = {
  cdp_playwright: {
    eyebrow: 'CDP Playwright',
    title: 'Chrome CDP với profile riêng',
    description:
      'Backend mở Chrome bằng CDP và sử dụng profile đăng nhập riêng. Nếu phát hiện checkpoint hoặc CAPTCHA, chế độ có giao diện sẽ chờ bạn xử lý thủ công; chế độ headless sẽ dừng lượt quét.',
    details: [
      'Profile: data/profiles/cdp_playwright_fb',
      'Báo lỗi khi session hết hạn hoặc tài khoản không có quyền xem group',
      'Dừng khi đủ số bài, đủ số lần cuộn hoặc hai vòng không có bài mới',
    ],
    profile: 'Persistent Chrome user data',
  },
  playwright: {
    eyebrow: 'Playwright',
    title: 'Persistent context và storage state',
    description:
      'Backend mở trình duyệt để bạn đăng nhập thủ công, sau đó lưu persistent profile và storage state. Khi session hết hạn hoặc group yêu cầu quyền truy cập, backend báo lỗi cho group đó.',
    details: [
      'Profile: data/profiles/playwright_fb',
      'Storage state: data/profiles/playwright_fb/storage_state.json',
      'Dừng khi đủ số bài, đủ số lần cuộn hoặc hai vòng không có bài mới',
    ],
    profile: 'Profile + storage_state.json',
  },
  seleniumbase: {
    eyebrow: 'SeleniumBase UC',
    title: 'Chrome UC với user data riêng',
    description:
      'Backend chạy SeleniumBase ở UC Mode với thư mục user data riêng. Engine gọi cơ chế xử lý CAPTCHA bằng giao diện khi mở group và trong từng vòng cuộn, sau đó kiểm tra lại session Facebook.',
    details: [
      'Profile: data/profiles/seleniumbase_fb',
      'Báo lỗi khi session Facebook đã hết hạn',
      'Dừng khi đủ số bài hoặc đủ số lần cuộn đã cấu hình',
    ],
    profile: 'SeleniumBase Chrome user data',
  },
};

function Toggle({ checked, onChange, label, description }: { checked: boolean; onChange: (value: boolean) => void; label: string; description: string }) {
  return (
    <button type="button" onClick={() => onChange(!checked)} className="flex w-full items-center justify-between gap-4 rounded-2xl border border-[#e2e5df] bg-[#fafbf8] p-4 text-left transition hover:border-[#c8d1cb]">
      <span>
        <span className="block text-sm font-semibold">{label}</span>
        <span className="mt-1 block text-[11px] text-[#89918e]">{description}</span>
      </span>
      <span className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${checked ? 'bg-[#16776f]' : 'bg-[#cbd2cd]'}`}>
        <span className={`absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
      </span>
    </button>
  );
}

function SafetyPanel({ engine }: { engine: EngineName }) {
  const content = engineSafety[engine];
  const container = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.07, delayChildren: 0.08 } },
  };
  const item = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.38, ease: [0.22, 1, 0.36, 1] as const } },
  };

  return (
    <motion.section
      key={engine}
      initial={{ opacity: 0, y: 12, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 220, damping: 25, mass: 0.8 }}
      whileHover={{ y: -3, boxShadow: '0 24px 58px rgba(16,43,42,.22)' }}
      className="relative isolate min-h-[430px] overflow-hidden rounded-[20px] border border-white/5 bg-[#102b2a] p-6 text-white shadow-[0_18px_50px_rgba(16,43,42,.16)]"
    >
      <motion.div
        className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-[#16776f]/45 blur-[90px]"
        animate={{ opacity: [0.55, 0.8, 0.55], scale: [1, 1.04, 1] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div
        className="absolute inset-0 opacity-[0.045]"
        style={{
          backgroundImage: 'linear-gradient(rgba(255,255,255,.7) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.7) 1px,transparent 1px)',
          backgroundSize: '36px 36px',
        }}
      />
      <motion.div
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#8fd0c4]/40 to-transparent"
        animate={{ top: ['12%', '88%', '12%'], opacity: [0, 0.55, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />

      <motion.div className="relative" variants={container} initial="hidden" animate="visible">
        <motion.div variants={item} className="flex items-center justify-between">
          <span className="grid h-11 w-11 place-items-center rounded-xl border border-white/10 bg-white/10 text-[#8fd0c4]">
            <ShieldCheck size={21} />
          </span>
          <span className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.055] px-3 py-1.5 text-[9px] font-bold uppercase tracking-[0.14em] text-white/55">
            <span className="soft-pulse h-1.5 w-1.5 rounded-full bg-[#8fd0c4]" />
            Backend behavior
          </span>
        </motion.div>

        <motion.p variants={item} className="mt-7 text-[11px] font-bold uppercase tracking-[0.16em] text-[#8fd0c4]">
          {content.eyebrow}
        </motion.p>
        <motion.h2 variants={item} className="mt-2 text-2xl font-medium tracking-[-0.04em]">
          {content.title}
        </motion.h2>
        <motion.p variants={item} className="mt-3 text-xs leading-6 text-white/58">
          {content.description}
        </motion.p>

        <motion.div variants={item} className="mt-6 flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.055] px-3 py-2.5">
          <FolderLock size={15} className="text-[#8fd0c4]" />
          <span className="text-[11px] font-medium text-white/68">{content.profile}</span>
        </motion.div>

        <motion.div variants={item} className="mt-6 space-y-3 border-t border-white/10 pt-5">
          {content.details.map(detail => (
            <div key={detail} className="group flex items-start gap-2.5 text-xs leading-5 text-white/64">
              <span className="mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded-full border border-[#8fd0c4]/65 text-[#8fd0c4] transition duration-300 group-hover:border-[#8fd0c4] group-hover:bg-[#8fd0c4] group-hover:text-[#102b2a]">
                <Check size={10} strokeWidth={3} />
              </span>
              <span className="transition-colors duration-300 group-hover:text-white/85">{detail}</span>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </motion.section>
  );
}

export function Scanner() {
  const { data: runtimeSettings } = useAsync(api.settings, []);
  const [engine, setEngine] = useState<EngineName>('cdp_playwright');
  const [maxScrolls, setMaxScrolls] = useState(8);
  const [maxPosts, setMaxPosts] = useState(30);
  const [sendTelegram, setSendTelegram] = useState(true);
  const [writeSheet, setWriteSheet] = useState(true);
  const [busy, setBusy] = useState(false);
  const [loginBusy, setLoginBusy] = useState(false);
  const [statusBusy, setStatusBusy] = useState(false);
  const [loginStatus, setLoginStatus] = useState<LoginStatus | null>(null);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const interactiveLoginAvailable = runtimeSettings?.interactive_login_available !== false;

  async function checkLogin() {
    setStatusBusy(true);
    setError(null);
    setNotice(null);
    try {
      const status = await api.loginStatus(engine);
      setLoginStatus(status);
      setNotice(status.logged_in ? 'Session Facebook đang hoạt động.' : status.message || 'Profile chưa đăng nhập hoặc session đã hết hạn.');
    } catch (err) {
      setLoginStatus(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setStatusBusy(false);
    }
  }

  async function login() {
    if (!interactiveLoginAvailable) {
      setError(null);
      setNotice('Backend Docker đang chạy headless. Hãy chạy backend trực tiếp trên Windows để mở cửa sổ đăng nhập Facebook.');
      return;
    }
    setLoginBusy(true);
    setError(null);
    setNotice(null);
    if (runtimeSettings?.browser_login_url) {
      window.open(runtimeSettings.browser_login_url, '_blank', 'noopener,noreferrer');
    }
    try {
      const status = await api.login(engine);
      setLoginStatus(status);
      setNotice(status.message || 'Đã lưu profile đăng nhập.');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoginBusy(false);
    }
  }

  async function run() {
    setBusy(true);
    setError(null);
    setNotice(null);
    setResult(null);
    try {
      const response = await api.scan({ engine, max_scrolls: maxScrolls, max_posts_per_group: maxPosts, send_telegram: sendTelegram, write_google_sheets: writeSheet });
      setResult(response);
      setNotice(response.status === 'success' ? 'Lượt quét đã hoàn tất.' : 'Lượt quét đã dừng với thông báo bên dưới.');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <Topbar title="Chạy quét Facebook" subtitle="Điều phối engine, giới hạn thu thập và kênh đồng bộ cho lượt quét tiếp theo." />
      <div className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
        <section className="card-premium p-5 md:p-6">
          <div className="flex items-center justify-between">
            <div><p className="eyebrow">Scan configuration</p><h2 className="mt-2 text-xl font-semibold tracking-[-0.03em]">Thiết lập lượt quét</h2></div>
            <Radar size={21} className="text-[#16776f]" />
          </div>
          <div className="mt-6 space-y-5">
            <label className="block"><span className="mb-2 block text-xs font-semibold text-[#52605d]">Engine</span>
              <select className="input" value={engine} disabled={busy || loginBusy || statusBusy} onChange={event => { setEngine(event.target.value as EngineName); setLoginStatus(null); setNotice(null); setError(null); }}>
                <option value="cdp_playwright">CDP Playwright</option>
                <option value="playwright">Playwright</option>
                <option value="seleniumbase">SeleniumBase</option>
              </select>
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label><span className="mb-2 block text-xs font-semibold text-[#52605d]">Số lần cuộn mỗi group</span><input className="input" type="number" min={1} max={80} value={maxScrolls} onChange={event => setMaxScrolls(Number(event.target.value))} /></label>
              <label><span className="mb-2 block text-xs font-semibold text-[#52605d]">Số bài tối đa mỗi group</span><input className="input" type="number" min={1} max={500} value={maxPosts} onChange={event => setMaxPosts(Number(event.target.value))} /></label>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Toggle checked={sendTelegram} onChange={setSendTelegram} label="Telegram alert" description="Gửi thông báo nếu được bật trong .env" />
              <Toggle checked={writeSheet} onChange={setWriteSheet} label="Google Sheets" description="Đồng bộ dữ liệu nếu được bật trong .env" />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button className="btn-soft" onClick={checkLogin} disabled={statusBusy || loginBusy || busy}>
                {statusBusy && <LoaderCircle size={16} className="animate-spin" />}
                {statusBusy ? 'Đang kiểm tra...' : 'Kiểm tra session'}
              </button>
              <button
                className="btn-soft"
                onClick={login}
                disabled={statusBusy || loginBusy || busy || !interactiveLoginAvailable}
                title={!interactiveLoginAvailable ? 'Cần chạy backend trực tiếp trên Windows để đăng nhập' : undefined}
              >
                {loginBusy ? <LoaderCircle size={16} className="animate-spin" /> : <LogIn size={16} />}
                {loginBusy ? 'Đang chờ đăng nhập...' : interactiveLoginAvailable ? 'Mở màn hình đăng nhập' : 'Không có màn hình đăng nhập'}
              </button>
              {loginStatus && <span className={`badge ${loginStatus.logged_in ? 'badge-success' : 'badge-warning'}`}>{loginStatus.logged_in ? 'Session sẵn sàng' : 'Chưa đăng nhập'}</span>}
            </div>
            {!interactiveLoginAvailable && (
              <p className="rounded-xl border border-[#ead5bd] bg-[#fff8ed] px-4 py-3 text-xs leading-5 text-[#8a572d]">
                Container Docker không có màn hình để mở Facebook. Kiểm tra session và quét headless vẫn hoạt động với profile đã đăng nhập; để tạo session mới, chạy backend trực tiếp trên Windows.
              </p>
            )}
            {interactiveLoginAvailable && runtimeSettings?.browser_login_url && (
              <a
                className="btn-soft w-fit"
                href={runtimeSettings.browser_login_url}
                target="_blank"
                rel="noreferrer"
              >
                Mở màn hình Docker noVNC
              </a>
            )}
            <button className="btn-primary min-h-12 w-full sm:w-auto" onClick={run} disabled={busy || loginBusy || statusBusy}>
              {busy ? <LoaderCircle size={17} className="animate-spin" /> : <Play size={17} />}
              {busy ? 'Đang quét dữ liệu...' : 'Chạy quét ngay'}
            </button>
          </div>
        </section>

        <SafetyPanel engine={engine} />
      </div>
      {notice && <div className="mt-5 rounded-2xl border border-[#b9ddd4] bg-[#eef9f6] p-4 text-sm font-semibold text-[#17685f]">{notice}</div>}
      {error && <div className="mt-5"><ErrorBox message={error} /></div>}
      {result && <section className="card-premium mt-5 overflow-hidden"><div className="border-b border-[#e4e7e1] px-5 py-4 text-sm font-semibold">Kết quả lượt quét</div><pre className="overflow-auto bg-[#102b2a] p-5 text-xs leading-6 text-white/75">{JSON.stringify(result, null, 2)}</pre></section>}
    </div>
  );
}
