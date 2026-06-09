import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, Database, Hash, Radio, TrendingUp, Users } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync, formatDate } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

function Stat({ label, value, icon: Icon }: { label: string; value: number; icon: any }) {
  return <div className="card-premium p-5"><div className="flex items-center justify-between"><div><div className="text-3xl font-black">{value.toLocaleString('vi-VN')}</div><div className="text-sm text-slate-500 font-semibold mt-1">{label}</div></div><div className="h-11 w-11 rounded-2xl bg-blue-50 text-[#0866FF] grid place-items-center"><Icon size={22}/></div></div></div>;
}

export function Dashboard() {
  const { data, loading, error, reload } = useAsync(api.dashboard, []);
  if (loading) return <Loading />;
  if (error || !data) return <ErrorBox message={error || 'Không có dữ liệu'} />;
  return (
    <div>
      <Topbar title="Dashboard Facebook Group Scraper" subtitle="Tổng quan group, keyword, bài viết, run history và lỗi hệ thống." onRefresh={reload} />
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 mb-5">
        <Stat label="Groups active" value={data.groups_active} icon={Users} />
        <Stat label="Keywords" value={data.keywords_total} icon={Hash} />
        <Stat label="Total posts" value={data.posts_total} icon={Database} />
        <Stat label="Posts today" value={data.posts_today} icon={TrendingUp} />
        <Stat label="Runs" value={data.runs_total} icon={Radio} />
        <Stat label="Errors" value={data.errors_total} icon={AlertTriangle} />
      </div>
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="card-premium p-5 h-[330px]"><h3 className="font-black mb-4">Bài viết 7 ngày gần nhất</h3><ResponsiveContainer width="100%" height="85%"><BarChart data={data.daily_posts}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="value" name="Posts" fill="#0866FF" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div>
        <div className="card-premium p-5"><h3 className="font-black mb-4">Lần quét gần nhất</h3>{data.last_run ? <div className="space-y-3 text-sm"><div className="flex justify-between"><span>Status</span><span className="badge badge-info">{data.last_run.status}</span></div><div className="flex justify-between"><span>Engine</span><b>{data.last_run.engine}</b></div><div className="flex justify-between"><span>Started</span><b>{formatDate(data.last_run.started_at)}</b></div><div className="flex justify-between"><span>Groups</span><b>{data.last_run.groups_success}/{data.last_run.groups_total}</b></div><div className="flex justify-between"><span>Inserted posts</span><b>{data.last_run.posts_inserted}</b></div><p className="text-slate-500 pt-2">{data.last_run.message}</p></div> : <Empty title="Chưa có lần quét" desc="Vào Run Scanner để chạy lần đầu." />}</div>
      </div>
      <div className="card-premium p-5 mt-5"><h3 className="font-black mb-4">Bài viết mới nhất</h3>{data.recent_posts.length ? <div className="space-y-3">{data.recent_posts.map(p => <div key={p.id} className="border border-slate-100 rounded-xl p-3"><div className="flex justify-between gap-4"><b>{p.group_name || 'Facebook Group'}</b><span className="text-xs text-slate-400">{formatDate(p.created_at)}</span></div><p className="text-sm text-slate-600 mt-1 line-clamp-2">{p.content}</p></div>)}</div> : <Empty title="Chưa có bài viết" desc="Thêm group và keyword, sau đó chạy scanner." />}</div>
    </div>
  );
}
