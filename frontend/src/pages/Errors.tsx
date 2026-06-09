import { api } from '../lib/api';
import { useAsync, formatDate } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

export function Errors() { const {data,loading,error,reload}=useAsync(api.errors,[]); return <div><Topbar title="Error Logs" subtitle="Log lỗi từng group, kèm đường dẫn thư mục screenshot nếu có." onRefresh={reload}/>{loading?<Loading/>:error?<ErrorBox message={error}/>:data?.length?<div className="space-y-3">{data.map(e=><div className="card-premium p-4" key={e.id}><div className="flex justify-between gap-3"><b className="text-red-700">{e.engine || 'engine'}</b><span className="text-xs text-slate-400">{formatDate(e.created_at)}</span></div><p className="text-sm text-slate-500 mt-1 break-all">{e.group_url}</p><p className="text-sm text-slate-800 mt-3 whitespace-pre-wrap">{e.error_message}</p>{e.screenshot_path && <p className="text-xs text-slate-400 mt-2">Screenshot dir: {e.screenshot_path}</p>}</div>)}</div>:<Empty title="Không có lỗi" desc="Hệ thống chưa ghi nhận lỗi quét group."/>}</div>; }
