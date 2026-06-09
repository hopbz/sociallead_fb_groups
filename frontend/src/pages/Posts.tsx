import { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync, formatDate } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

export function Posts() {
  const [q, setQ] = useState('');
  const { data, loading, error, reload } = useAsync(() => api.posts(q), [q]);
  return <div><Topbar title="Scraped Posts" subtitle="Danh sách bài viết đã qua anti-duplicate và keyword filter." onRefresh={reload}/><div className="card-premium p-4 mb-5"><input className="input" placeholder="Tìm trong nội dung bài viết..." value={q} onChange={e=>setQ(e.target.value)}/></div>{loading ? <Loading/> : error ? <ErrorBox message={error}/> : data?.length ? <div className="space-y-4">{data.map(p=><article key={p.id} className="card-premium p-5"><div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3"><div><h3 className="font-black">{p.group_name || 'Facebook Group'}</h3><div className="text-xs text-slate-400 mt-1">{formatDate(p.created_at)} • {p.engine} • {p.author || 'Unknown author'}</div></div><div className="flex gap-2">{p.matched_keywords && <span className="badge badge-info">{p.matched_keywords}</span>}{p.post_url && <a href={p.post_url} target="_blank" className="btn-soft"><ExternalLink size={16}/>Mở</a>}</div></div><p className="text-sm leading-6 text-slate-700 mt-4 whitespace-pre-wrap">{p.content}</p></article>)}</div> : <Empty title="Chưa có bài viết" desc="Chạy scanner để có dữ liệu."/>}</div>;
}
