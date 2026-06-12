import { useState } from 'react';
import { motion } from 'motion/react';
import { Clock3, Database, Gauge, LogOut, Play, Settings, Users } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Groups } from './pages/Groups';
import { Posts } from './pages/Posts';
import { Scanner } from './pages/Scanner';
import { Settings as SettingsPage } from './pages/Settings';
import { History } from './pages/History';
import { Auth } from './pages/Auth';
import { clearApiConnection, getApiToken } from './lib/api';

const mobileItems = [
  { id: 'dashboard', label: 'Tổng quan', icon: Gauge },
  { id: 'groups', label: 'Groups', icon: Users },
  { id: 'scanner', label: 'Quét', icon: Play },
  { id: 'history', label: 'Lịch sử', icon: Clock3 },
  { id: 'posts', label: 'Bài viết', icon: Database },
  { id: 'settings', label: 'Cấu hình', icon: Settings },
];

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getApiToken()));
  const [active, setActive] = useState('dashboard');

  const render = () => {
    if (active === 'groups') return <Groups />;
    if (active === 'posts') return <Posts />;
    if (active === 'scanner') return <Scanner />;
    if (active === 'history') return <History />;
    if (active === 'settings') return <SettingsPage />;
    return <Dashboard />;
  };

  if (!isAuthenticated) return <Auth onLogin={() => setIsAuthenticated(true)} />;

  function logout() {
    clearApiConnection();
    setIsAuthenticated(false);
  }

  return (
    <div className="app-canvas min-h-screen md:grid md:grid-cols-[248px_1fr]">
      <div className="fixed inset-y-0 left-0 z-40 hidden w-[248px] md:block">
        <Sidebar active={active} setActive={setActive} onLogout={logout} />
      </div>

      <main className="min-w-0 md:col-start-2">
        <div className="mx-auto w-full max-w-[1500px] px-4 py-6 pb-28 sm:px-6 md:px-8 md:py-9 md:pb-10 lg:px-10">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
          >
            {render()}
          </motion.div>
        </div>
      </main>

      <nav className="fixed bottom-3 left-3 right-3 z-50 flex items-center justify-between gap-1 rounded-2xl border border-[#dfe3dc] bg-white/92 p-2 shadow-[0_18px_50px_rgba(16,43,42,.18)] backdrop-blur-xl md:hidden">
        {mobileItems.map(item => {
          const Icon = item.icon;
          const selected = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActive(item.id)}
              className={`flex min-w-0 flex-1 flex-col items-center gap-1 rounded-xl px-2 py-2 text-[9px] font-bold transition ${
                selected ? 'bg-[#102b2a] text-white' : 'text-[#66706d] hover:bg-[#f0f2ee]'
              }`}
            >
              <Icon size={17} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
        <button onClick={logout} className="grid h-11 w-11 shrink-0 place-items-center rounded-xl text-[#bd4b43] hover:bg-[#fff4f2]" aria-label="Đăng xuất">
          <LogOut size={18} />
        </button>
      </nav>
    </div>
  );
}
