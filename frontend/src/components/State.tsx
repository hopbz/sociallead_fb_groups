import { AlertCircle, Inbox, LoaderCircle } from 'lucide-react';

export function Loading() {
  return (
    <div className="card-premium grid min-h-40 place-items-center p-8 text-center">
      <div>
        <LoaderCircle className="soft-pulse mx-auto animate-spin text-[#16776f]" size={28} />
        <p className="mt-3 text-sm font-semibold text-[#66706d]">Đang tải dữ liệu...</p>
      </div>
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="flex gap-3 rounded-2xl border border-[#efc7c2] bg-[#fff4f2] p-4 text-sm font-semibold text-[#a33f38]">
      <AlertCircle className="mt-0.5 shrink-0" size={18} />
      <span className="whitespace-pre-wrap">{message}</span>
    </div>
  );
}

export function Empty({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="card-premium py-14 text-center">
      <span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-[#e1e8e6] text-[#16776f]">
        <Inbox size={22} />
      </span>
      <h3 className="mt-4 text-base font-semibold text-[#253331]">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#7d8784]">{desc}</p>
    </div>
  );
}
