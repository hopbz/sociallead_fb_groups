import { RefreshCw, Sparkles } from 'lucide-react';

type Props = { title: string; subtitle: string; onRefresh?: () => void };

export function Topbar({ title, subtitle, onRefresh }: Props) {
  return (
    <header className="mb-7 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Sparkles size={15} className="text-[#16776f]" />
          <span className="eyebrow">Social intelligence workspace</span>
        </div>
        <h1 className="text-3xl font-semibold tracking-[-0.045em] text-[#14201f] md:text-[40px] md:leading-[1.06]">{title}</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-[#66706d]">{subtitle}</p>
      </div>
      {onRefresh && (
        <button className="btn-soft shrink-0" onClick={onRefresh}>
          <RefreshCw size={16} />
          Làm mới
        </button>
      )}
    </header>
  );
}
