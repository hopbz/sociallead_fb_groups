import { Clock3, Database, Gauge, LogOut, Play, Radio, Settings, Users } from 'lucide-react';

type Props = { active: string; setActive: (tab: string) => void; onLogout: () => void };

const items = [
  { id: 'dashboard', label: 'Tổng quan', icon: Gauge },
  { id: 'groups', label: 'Facebook Groups', icon: Users },
  { id: 'posts', label: 'Bài viết đã quét', icon: Database },
  { id: 'scanner', label: 'Chạy quét', icon: Play },
  { id: 'history', label: 'Lịch sử quét', icon: Clock3 },
  { id: 'settings', label: 'Cấu hình', icon: Settings },
];

export function Sidebar({ active, setActive, onLogout }: Props) {
  return (
    <aside className="flex h-full w-full flex-col bg-[#102b2a] px-4 py-5 text-white">
      <div className="flex items-center gap-3 px-2">
        <span className="grid h-11 w-11 place-items-center rounded-xl bg-[#d9eee9] text-[#102b2a] shadow-lg shadow-black/10">
          <Radio size={22} strokeWidth={2.2} />
        </span>
        <span>
          <span className="block text-[16px] font-semibold tracking-[-0.03em]">SocialLead OS</span>
          <span className="block text-[11px] text-white/45">Facebook Intelligence</span>
        </span>
      </div>

      <div className="mt-8 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-white/35">Workspace</div>
      <nav className="mt-3 flex-1 min-h-0 space-y-1 overflow-y-auto">
        {items.map(item => {
          const Icon = item.icon;
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActive(item.id)}
              className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-300 ease-out ${
                isActive
                  ? 'translate-x-0 bg-white text-[#102b2a] shadow-[0_10px_24px_rgba(0,0,0,0.12)]'
                  : 'text-white/62 hover:translate-x-0.5 hover:bg-white/[0.07] hover:text-white'
              }`}
            >
              <Icon className="h-[18px] w-[18px] transition-transform duration-300 group-hover:scale-110" strokeWidth={1.8} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="shrink-0">
        <div className="mb-3 rounded-2xl border border-white/10 bg-white/[0.05] p-3">
          <div className="mb-3 flex items-center gap-3">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-[#e7763d] text-xs font-bold">SL</span>
            <span className="min-w-0">
              <span className="block truncate text-xs font-semibold">SocialLead Admin</span>
              <span className="block truncate text-[11px] text-white/42">Local workspace</span>
            </span>
          </div>
          <div className="flex items-center justify-between border-t border-white/10 pt-2.5">
            <span className="rounded-md bg-white/10 px-2 py-1 text-[9px] font-bold tracking-[0.12em] text-white/70">ONLINE</span>
            <button onClick={onLogout} className="flex items-center gap-1.5 text-[11px] font-medium text-white/45 transition hover:text-white">
              <LogOut size={14} />
              Đăng xuất
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 text-[10px] text-white/35">
          <span className="soft-pulse h-1.5 w-1.5 rounded-full bg-emerald-400" />
          Hệ thống đang hoạt động
        </div>
      </div>
    </aside>
  );
}
