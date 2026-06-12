import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, Database, Hash, TrendingUp, Users } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync, formatDate } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

const accents = {
  navy: 'bg-[#e1e8e6] text-[#102b2a]',
  teal: 'bg-[#d9eee9] text-[#16776f]',
  orange: 'bg-[#fbe5d9] text-[#c45726]',
};

function Stat({ label, value, icon: Icon, detail, accent }: { label: string; value: number; icon: typeof Users; detail: string; accent: keyof typeof accents }) {
  return (
    <div className="card-premium interactive-card group p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-[#66706d]">{label}</p>
          <p className="mt-2 text-[32px] font-semibold leading-none tracking-[-0.05em]">{value.toLocaleString('vi-VN')}</p>
        </div>
        <span className={`grid h-10 w-10 place-items-center rounded-xl transition-transform duration-300 group-hover:rotate-3 group-hover:scale-105 ${accents[accent]}`}>
          <Icon size={18} strokeWidth={1.9} />
        </span>
      </div>
      <p className="mt-4 text-[11px] text-[#89918e]">{detail}</p>
    </div>
  );
}

export function Dashboard() {
  const { data, loading, error, reload } = useAsync(api.dashboard, []);
  if (loading) return <Loading />;
  if (error || !data) return <ErrorBox message={error || 'Không có dữ liệu'} />;

  return (
    <div>
      <Topbar title="Trung tâm điều hành" subtitle="Theo dõi nguồn group, bộ lọc và nội dung thu thập trong một không gian thống nhất." onRefresh={reload} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Group đang hoạt động" value={data.groups_active} icon={Users} detail={`${data.groups_total} group trong hệ thống`} accent="navy" />
        <Stat label="Keyword đã chọn" value={data.keywords_total} icon={Hash} detail="Bộ lọc nội dung theo thời gian thực" accent="teal" />
        <Stat label="Tổng bài viết" value={data.posts_total} icon={Database} detail="Đã chống trùng lặp dữ liệu" accent="orange" />
        <Stat label="Bài viết hôm nay" value={data.posts_today} icon={TrendingUp} detail="Cập nhật từ các lượt quét mới nhất" accent="teal" />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.35fr_.65fr]">
        <section className="card-premium p-5 md:p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="eyebrow">Content pulse</p>
              <h2 className="mt-2 text-xl font-semibold tracking-[-0.03em]">Bài viết 7 ngày gần nhất</h2>
            </div>
            <TrendingUp size={20} className="text-[#16776f]" />
          </div>
          <div className="mt-6 h-[285px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.daily_posts}>
                <CartesianGrid stroke="#e4e7e1" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: '#7d8784', fontSize: 11 }} />
                <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#7d8784', fontSize: 11 }} />
                <Tooltip cursor={{ fill: '#f4f5f0' }} contentStyle={{ border: '1px solid #dfe3dc', borderRadius: 12, boxShadow: '0 12px 32px rgba(16,43,42,.08)' }} />
                <Bar dataKey="value" name="Bài viết" fill="#16776f" radius={[7, 7, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="relative overflow-hidden rounded-[20px] bg-[#102b2a] p-6 text-white shadow-[0_16px_40px_rgba(16,43,42,.12)]">
          <div className="absolute -right-16 -top-16 h-52 w-52 rounded-full bg-[#16776f]/45 blur-[70px]" />
          <div className="relative">
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-white/42">System signal</p>
            <p className="mt-8 text-5xl font-medium tracking-[-0.06em]">{data.groups_active}</p>
            <p className="mt-2 text-xs text-white/50">Nguồn group đang được theo dõi</p>
            <div className="mt-8 h-1.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-[#8fd0c4]" style={{ width: `${Math.min(100, data.groups_total ? (data.groups_active / data.groups_total) * 100 : 0)}%` }} />
            </div>
            <div className="mt-8 flex items-center justify-between border-t border-white/10 pt-4 text-xs">
              <span className="text-white/45">{data.keywords_total} keyword hoạt động</span>
              <span className="flex items-center gap-1 font-semibold">Live <ArrowUpRight size={14} /></span>
            </div>
          </div>
        </section>
      </div>

      <section className="card-premium mt-5 overflow-hidden">
        <div className="flex items-center justify-between border-b border-[#e4e7e1] px-5 py-4">
          <div><p className="text-sm font-semibold">Bài viết mới nhất</p><p className="mt-1 text-[11px] text-[#89918e]">Nội dung vừa được thu thập</p></div>
          <Database size={19} className="text-[#e7763d]" />
        </div>
        {data.recent_posts.length ? (
          <div className="divide-y divide-[#e8eae5]">
            {data.recent_posts.map((post, index) => (
              <div key={post.id} className="row-reveal px-5 py-4 transition-colors hover:bg-[#fafbf8]" style={{ '--row-index': index } as React.CSSProperties}>
                <div className="flex flex-col justify-between gap-2 sm:flex-row">
                  <p className="text-sm font-semibold text-[#253331]">{post.group_name || 'Facebook Group'}</p>
                  <span className="text-[10px] text-[#89918e]">{formatDate(post.created_at)}</span>
                </div>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-[#66706d]">{post.content}</p>
              </div>
            ))}
          </div>
        ) : <div className="p-5"><Empty title="Chưa có bài viết" desc="Thêm group và keyword, sau đó chạy scanner." /></div>}
      </section>
    </div>
  );
}
