import { RefreshCw } from 'lucide-react';

type Props = { title: string; subtitle: string; onRefresh?: () => void };

export function Topbar({ title, subtitle, onRefresh }: Props) {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-950">{title}</h1>
        <p className="text-sm text-slate-500 mt-1">{subtitle}</p>
      </div>
      {onRefresh && <button className="btn-soft" onClick={onRefresh}><RefreshCw size={17} /> Refresh</button>}
    </div>
  );
}
