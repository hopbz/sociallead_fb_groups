export function Loading() { return <div className="card-premium p-8 text-center text-slate-500 font-bold">Đang tải dữ liệu...</div>; }
export function ErrorBox({ message }: { message: string }) { return <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700 text-sm font-semibold whitespace-pre-wrap">{message}</div>; }
export function Empty({ title, desc }: { title: string; desc: string }) { return <div className="card-premium p-10 text-center"><h3 className="font-black text-lg">{title}</h3><p className="text-slate-500 text-sm mt-1">{desc}</p></div>; }
