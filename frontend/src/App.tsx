import { useState } from 'react';
import { LogOut } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Groups } from './pages/Groups';
import { Keywords } from './pages/Keywords';
import { Posts } from './pages/Posts';
import { Scanner } from './pages/Scanner';
import { Runs } from './pages/Runs';
import { Errors } from './pages/Errors';
import { Settings } from './pages/Settings';
import { Auth } from './pages/Auth';
import { clearApiConnection, getApiToken } from './lib/api';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getApiToken()));
  const [active, setActive] = useState('dashboard');

  const render = () => {
    if (active === 'groups') return <Groups />;
    if (active === 'keywords') return <Keywords />;
    if (active === 'posts') return <Posts />;
    if (active === 'scanner') return <Scanner />;
    if (active === 'runs') return <Runs />;
    if (active === 'errors') return <Errors />;
    if (active === 'settings') return <Settings />;
    return <Dashboard />;
  };

  if (!isAuthenticated) return <Auth onLogin={() => setIsAuthenticated(true)} />;

  function logout() {
    clearApiConnection();
    setIsAuthenticated(false);
  }

  return (
    <div className="h-screen bg-[#EBF1ED] flex overflow-hidden p-3 md:p-4 gap-4">
      <div className="hidden md:block w-[285px] rounded-3xl overflow-hidden border border-slate-200 shadow-sm"><Sidebar active={active} setActive={setActive}/></div>
      <div className="md:hidden fixed bottom-3 left-3 right-3 z-20 bg-white rounded-2xl border border-slate-200 shadow-lg p-2 overflow-x-auto"><div className="flex gap-2 min-w-max"><button className="btn-soft" onClick={()=>setActive('dashboard')}>Dashboard</button><button className="btn-soft" onClick={()=>setActive('groups')}>Groups</button><button className="btn-soft" onClick={()=>setActive('scanner')}>Scan</button><button className="btn-soft" onClick={()=>setActive('posts')}>Posts</button><button className="btn-soft" onClick={logout}><LogOut size={16}/>Logout</button></div></div>
      <main className="flex-1 overflow-y-auto rounded-3xl bg-transparent p-2 md:p-4 pb-24 md:pb-4 relative">
        <button onClick={logout} className="hidden md:inline-flex fixed top-5 right-6 z-10 btn-soft"><LogOut size={16}/>Logout</button>
        {render()}
      </main>
    </div>
  );
}
