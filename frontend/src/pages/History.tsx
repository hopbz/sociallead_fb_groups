import { useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, ChevronDown, Clock3, Database, RefreshCw, XCircle } from 'lucide-react';
import { api, type ErrorLog, type Run } from '../lib/api';
import { formatDate, useAsync } from '../lib/hooks';
import { Empty, ErrorBox, Loading } from '../components/State';
import { Topbar } from '../components/Topbar';

type HistoryData = { runs: Run[]; errors: ErrorLog[] };

const statusMeta: Record<string, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  success: { label: 'Thành công', className: 'badge-success', icon: CheckCircle2 },
  partial_failed: { label: 'Một phần', className: 'badge-warning', icon: AlertTriangle },
  failed: { label: 'Thất bại', className: 'badge-danger', icon: XCircle },
  running: { label: 'Đang chạy', className: 'badge-info', icon: Clock3 },
};

function duration(run: Run) {
  if (!run.finished_at) return '-';
  const seconds = Math.max(0, Math.round((new Date(run.finished_at).getTime() - new Date(run.started_at).getTime()) / 1000));
  if (seconds < 60) return `${seconds} giây`;
  return `${Math.floor(seconds / 60)} phút ${seconds % 60} giây`;
}

export function History() {
  const { data, loading, error, reload } = useAsync<HistoryData>(
    async () => {
      const [runs, errors] = await Promise.all([api.runs(), api.errors()]);
      return { runs, errors };
    },
    [],
  );
  const [expanded, setExpanded] = useState<string | null>(null);

  const errorsByRun = useMemo(() => {
    const map = new Map<string, ErrorLog[]>();
    for (const item of data?.errors || []) {
      if (!item.run_id) continue;
      map.set(item.run_id, [...(map.get(item.run_id) || []), item]);
    }
    return map;
  }, [data]);

  if (loading) return <Loading />;
  if (error || !data) return <ErrorBox message={error || 'Không thể tải lịch sử quét.'} />;

  const successCount = data.runs.filter(run => run.status === 'success').length;
  const failedCount = data.runs.filter(run => run.status === 'failed').length;
  const insertedCount = data.runs.reduce((sum, run) => sum + run.posts_inserted, 0);

  return (
    <div>
      <Topbar
        title="Lịch sử quét"
        subtitle="Theo dõi từng lượt chạy, số group xử lý, bài viết thu thập và nguyên nhân lỗi."
        onRefresh={reload}
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card-premium p-5"><p className="text-xs text-[#66706d]">Tổng lượt quét</p><p className="mt-2 text-3xl font-semibold">{data.runs.length}</p></div>
        <div className="card-premium p-5"><p className="text-xs text-[#66706d]">Thành công / thất bại</p><p className="mt-2 text-3xl font-semibold"><span className="text-[#16776f]">{successCount}</span> / <span className="text-[#bd4b43]">{failedCount}</span></p></div>
        <div className="card-premium p-5"><p className="text-xs text-[#66706d]">Bài viết đã lưu</p><p className="mt-2 text-3xl font-semibold">{insertedCount.toLocaleString('vi-VN')}</p></div>
      </div>

      <section className="card-premium mt-5 overflow-hidden">
        <div className="flex items-center justify-between border-b border-[#e4e7e1] px-5 py-4">
          <div><p className="text-sm font-semibold">Các lượt quét gần đây</p><p className="mt-1 text-[11px] text-[#89918e]">Hiển thị tối đa 100 lượt gần nhất</p></div>
          <button className="btn-soft !px-3 !py-2" onClick={reload}><RefreshCw size={15} />Làm mới</button>
        </div>

        {data.runs.length ? (
          <div className="divide-y divide-[#e8eae5]">
            {data.runs.map((run, index) => {
              const meta = statusMeta[run.status] || statusMeta.running;
              const StatusIcon = meta.icon;
              const runErrors = errorsByRun.get(run.id) || [];
              const isExpanded = expanded === run.id;
              return (
                <article key={run.id} className="row-reveal" style={{ '--row-index': index } as React.CSSProperties}>
                  <button
                    className="grid w-full gap-4 px-5 py-4 text-left transition hover:bg-[#fafbf8] lg:grid-cols-[1.1fr_.8fr_1fr_1fr_auto]"
                    onClick={() => setExpanded(isExpanded ? null : run.id)}
                    aria-expanded={isExpanded}
                  >
                    <span><span className="block text-sm font-semibold">{formatDate(run.started_at)}</span><span className="mt-1 block text-[11px] text-[#89918e]">{run.engine} · {duration(run)}</span></span>
                    <span><span className={`badge ${meta.className}`}><StatusIcon size={13} />{meta.label}</span></span>
                    <span className="text-xs text-[#66706d]"><strong className="text-[#253331]">{run.groups_success}/{run.groups_total}</strong> group thành công</span>
                    <span className="text-xs text-[#66706d]"><strong className="text-[#253331]">{run.posts_inserted}</strong> bài mới · {run.posts_seen} đã thấy</span>
                    <ChevronDown size={18} className={`text-[#89918e] transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                  </button>

                  {isExpanded && (
                    <div className="border-t border-[#edf0eb] bg-[#fafbf8] px-5 py-4">
                      <div className="grid gap-3 sm:grid-cols-3">
                        <div className="rounded-xl bg-white p-3 text-xs"><Database size={15} className="mb-2 text-[#16776f]" />Khớp keyword: <strong>{run.posts_matched}</strong></div>
                        <div className="rounded-xl bg-white p-3 text-xs">Group lỗi: <strong>{run.groups_failed}</strong></div>
                        <div className="rounded-xl bg-white p-3 text-xs">Run ID: <span className="break-all font-mono text-[10px]">{run.id}</span></div>
                      </div>
                      {run.message && <p className="mt-3 rounded-xl border border-[#e4e7e1] bg-white p-3 text-xs leading-5 text-[#66706d]">{run.message}</p>}
                      {runErrors.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {runErrors.map(item => (
                            <div key={item.id} className="rounded-xl border border-[#efc7c2] bg-[#fff4f2] p-3 text-xs leading-5 text-[#a33f38]">
                              {item.group_url && <p className="mb-1 break-all font-semibold">{item.group_url}</p>}
                              {item.error_message}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        ) : <div className="p-5"><Empty title="Chưa có lịch sử quét" desc="Chạy scanner để tạo lượt quét đầu tiên." /></div>}
      </section>
    </div>
  );
}
