import { useMemo, useState } from 'react';
import { Check, Copy, ExternalLink, Search, Sparkles } from 'lucide-react';
import { api } from '../lib/api';
import type { LeadStatus } from '../lib/api';
import { formatDate, useAsync } from '../lib/hooks';
import { Empty, ErrorBox, Loading } from '../components/State';
import { Topbar } from '../components/Topbar';

const statuses: { value: LeadStatus; label: string }[] = [
  { value: 'new', label: 'Mới' },
  { value: 'reviewed', label: 'Đã review' },
  { value: 'contacted', label: 'Đã liên hệ' },
  { value: 'won', label: 'Thành công' },
  { value: 'lost', label: 'Không phù hợp' },
];

function scoreStyle(score: number) {
  if (score >= 9) return 'bg-[#102b2a] text-white';
  if (score >= 7) return 'bg-[#e7763d] text-white';
  return 'bg-[#e1e8e6] text-[#52605d]';
}

export function Leads() {
  const [minimumScore, setMinimumScore] = useState(7);
  const [status, setStatus] = useState<LeadStatus | ''>('');
  const [query, setQuery] = useState('');
  const [copiedId, setCopiedId] = useState('');
  const [busyId, setBusyId] = useState('');
  const [actionError, setActionError] = useState('');
  const { data, loading, error, reload } = useAsync(
    () => api.leads({ minScore: minimumScore, status, q: query.trim() }),
    [minimumScore, status, query],
  );

  const summary = useMemo(() => {
    const leads = data ?? [];
    return {
      total: leads.length,
      hot: leads.filter(lead => lead.score >= 9).length,
      new: leads.filter(lead => lead.status === 'new').length,
    };
  }, [data]);

  async function copyComment(id: string, comment: string) {
    await navigator.clipboard.writeText(comment);
    setCopiedId(id);
    window.setTimeout(() => setCopiedId(current => current === id ? '' : current), 1800);
  }

  async function changeStatus(id: string, nextStatus: LeadStatus) {
    setBusyId(id);
    setActionError('');
    try {
      await api.updateLeadStatus(id, nextStatus);
      await reload();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyId('');
    }
  }

  return (
    <div>
      <Topbar
        title="Lead tiềm năng"
        subtitle="Review các cơ hội được AI chấm điểm trước khi quyết định liên hệ thủ công."
        onRefresh={reload}
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-3">
        {[
          ['Lead đang hiển thị', summary.total],
          ['Lead rất nóng', summary.hot],
          ['Chờ review', summary.new],
        ].map(([label, value]) => (
          <div key={String(label)} className="card-premium p-4">
            <p className="text-xs font-semibold text-[#7d8784]">{label}</p>
            <p className="mt-2 text-2xl font-bold tracking-[-0.04em] text-[#102b2a]">{value}</p>
          </div>
        ))}
      </div>

      <section className="card-premium mb-5 grid gap-3 p-4 md:grid-cols-[1fr_180px_180px]">
        <label className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[#89918e]" size={17} />
          <input
            className="input search-input"
            placeholder="Tìm theo group, tác giả, nội dung..."
            value={query}
            onChange={event => setQuery(event.target.value)}
          />
        </label>
        <select className="input" value={minimumScore} onChange={event => setMinimumScore(Number(event.target.value))}>
          <option value={1}>Tất cả score</option>
          <option value={7}>Score từ 7</option>
          <option value={8}>Score từ 8</option>
          <option value={9}>Score từ 9</option>
        </select>
        <select className="input" value={status} onChange={event => setStatus(event.target.value as LeadStatus | '')}>
          <option value="">Tất cả trạng thái</option>
          {statuses.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
        </select>
      </section>

      {actionError && <div className="mb-5"><ErrorBox message={actionError} /></div>}

      {loading ? <Loading /> : error ? <ErrorBox message={error} /> : data?.length ? (
        <div className="space-y-4">
          {data.map((lead, index) => (
            <article
              key={lead.id}
              className="card-premium interactive-card row-reveal overflow-hidden"
              style={{ '--row-index': index } as React.CSSProperties}
            >
              <div className="grid md:grid-cols-[110px_1fr]">
                <div className="flex items-center justify-center border-b border-[#dfe3dc] p-5 md:border-b-0 md:border-r">
                  <div className={`grid h-20 w-20 place-items-center rounded-[22px] ${scoreStyle(lead.score)}`}>
                    <span className="text-center">
                      <strong className="block text-3xl tracking-[-0.06em]">{lead.score}</strong>
                      <span className="text-[10px] font-bold uppercase tracking-[0.14em] opacity-75">Score</span>
                    </span>
                  </div>
                </div>
                <div className="p-5 md:p-6">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="badge badge-success">{lead.need_stage || 'unknown'}</span>
                        <span className="badge badge-info">{statuses.find(item => item.value === lead.status)?.label}</span>
                        {lead.score >= 9 && <span className="badge badge-warning"><Sparkles size={12} />Ưu tiên cao</span>}
                      </div>
                      <h2 className="mt-3 text-lg font-semibold tracking-[-0.025em]">{lead.group_name || 'Facebook Group'}</h2>
                      <p className="mt-1 text-xs text-[#89918e]">
                        {lead.author || 'Không rõ tác giả'} · {formatDate(lead.created_at)}
                      </p>
                    </div>
                    <select
                      className="input !w-auto min-w-40"
                      value={lead.status}
                      disabled={busyId === lead.id}
                      onChange={event => void changeStatus(lead.id, event.target.value as LeadStatus)}
                    >
                      {statuses.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
                    </select>
                  </div>

                  <p className="mt-5 line-clamp-4 whitespace-pre-wrap text-sm leading-7 text-[#52605d]">{lead.content}</p>

                  <div className="mt-5 grid gap-3 lg:grid-cols-2">
                    <div className="rounded-2xl bg-[#f4f5f0] p-4">
                      <p className="eyebrow">Lý do chấm điểm</p>
                      <p className="mt-2 text-sm leading-6 text-[#52605d]">{lead.reason || 'Chưa có lý do.'}</p>
                    </div>
                    <div className="rounded-2xl border border-[#b9ddd4] bg-[#eef9f6] p-4">
                      <p className="eyebrow">Comment đề xuất</p>
                      <p className="mt-2 text-sm leading-6 text-[#31514d]">{lead.suggested_comment}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <button className="btn-primary" onClick={() => void copyComment(lead.id, lead.suggested_comment)}>
                      {copiedId === lead.id ? <Check size={16} /> : <Copy size={16} />}
                      {copiedId === lead.id ? 'Đã copy' : 'Copy comment'}
                    </button>
                    {lead.post_url && (
                      <a className="btn-soft" href={lead.post_url} target="_blank" rel="noreferrer">
                        <ExternalLink size={16} />Mở bài viết
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <Empty
          title="Chưa có lead phù hợp"
          desc="Thử giảm ngưỡng score, đổi bộ lọc hoặc chạy workflow n8n để phân tích bài viết mới."
        />
      )}
    </div>
  );
}
