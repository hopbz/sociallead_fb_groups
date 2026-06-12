import { useEffect, useState } from 'react';
import { ExternalLink, Search } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync, formatDate } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

export function Posts() {
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const { data, loading, error, reload } = useAsync(() => api.posts(searchQuery), [searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => setSearchQuery(query.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [query]);

  return (
    <div>
      <Topbar title="Bài viết đã quét" subtitle="Kho nội dung đã chống trùng lặp và đi qua bộ lọc keyword." onRefresh={reload} />
      <div className="card-premium mb-5 p-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[#89918e]" size={17} />
          <input
            className="input search-input"
            type="search"
            aria-label="Tìm bài viết đã quét"
            placeholder="Tìm trong nội dung, tác giả, keyword hoặc group..."
            value={query}
            onChange={event => setQuery(event.target.value)}
          />
        </div>
      </div>
      {loading ? <Loading /> : error ? <ErrorBox message={error} /> : data?.length ? (
        <div className="space-y-4">
          {data.map((post, index) => (
            <article key={post.id} className="card-premium interactive-card row-reveal p-5 md:p-6" style={{ '--row-index': index } as React.CSSProperties}>
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="eyebrow">Facebook source</p>
                  <h2 className="mt-2 text-base font-semibold tracking-[-0.02em]">{post.group_name || 'Facebook Group'}</h2>
                  <p className="mt-1 text-[11px] text-[#89918e]">{formatDate(post.created_at)} · {post.engine} · {post.author || 'Không rõ tác giả'}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {post.matched_keywords && <span className="badge badge-success">#{post.matched_keywords}</span>}
                  {post.post_url && <a href={post.post_url} target="_blank" rel="noreferrer" className="btn-soft !px-3 !py-2"><ExternalLink size={15} />Mở bài viết</a>}
                </div>
              </div>
              <p className="mt-5 whitespace-pre-wrap text-sm leading-7 text-[#52605d]">{post.content}</p>
            </article>
          ))}
        </div>
      ) : <Empty title="Chưa có bài viết" desc="Chạy scanner để thu thập dữ liệu đầu tiên." />}
    </div>
  );
}
