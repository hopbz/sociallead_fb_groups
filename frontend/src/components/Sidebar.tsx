import { BarChart3, Database, FileWarning, Hash, LayoutDashboard, Play, Radio, Settings, Users } from 'lucide-react';

type Props = { active: string; setActive: (tab: string) => void };

const items = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'groups', label: 'Facebook Groups', icon: Users },
  { id: 'keywords', label: 'Keyword Filter', icon: Hash },
  { id: 'posts', label: 'Scraped Posts', icon: Database },
  { id: 'scanner', label: 'Run Scanner', icon: Play },
  { id: 'runs', label: 'Run History', icon: BarChart3 },
  { id: 'errors', label: 'Error Logs', icon: FileWarning },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ active, setActive }: Props) {
  return (
    <aside className="w-full h-full flex flex-col p-4 bg-white">
      <div className="flex items-center gap-3 px-2 pb-5 border-b border-slate-100">
        <div className="h-11 w-11 bg-[#0866FF] rounded-2xl text-white grid place-items-center shadow-sm"><Radio size={24} /></div>
        <div>
          <div className="text-xl font-black tracking-tight">SocialLead <span className="text-[#0866FF]">OS</span></div>
          <div className="text-xs font-bold text-slate-400 uppercase">Facebook Groups</div>
        </div>
      </div>
      <nav className="flex-1 pt-5 space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = active === item.id;
          return (
            <button key={item.id} onClick={() => setActive(item.id)} className={`w-full flex items-center gap-3 rounded-xl px-3 py-3 text-sm font800 transition ${isActive ? 'bg-blue-50 text-[#0866FF]' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}>
              <Icon size={19} />
              <span className="font-bold">{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="rounded-2xl bg-slate-50 p-3 text-xs text-slate-500 leading-relaxed">
        Chỉ scrape các group tài khoản của em có quyền xem. Không bypass checkpoint/CAPTCHA.
      </div>
    </aside>
  );
}
