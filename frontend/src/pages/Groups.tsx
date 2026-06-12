import { useEffect, useMemo, useState } from 'react';
import { Check, Hash, Link2, Plus, Trash2, Users } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

function normalizeGroupUrl(rawUrl: string) {
  const trimmed = rawUrl.trim();
  if (!trimmed) return '';
  const groupUrl = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
  try {
    const parsed = new URL(groupUrl);
    const pathParts = parsed.pathname.split('/').filter(Boolean);
    const groupsIndex = pathParts.findIndex(part => part.toLowerCase() === 'groups');
    const groupSlug = groupsIndex >= 0 ? pathParts[groupsIndex + 1] : '';
    if (groupSlug) return `https://www.facebook.com/groups/${groupSlug}`;
  } catch {
    return groupUrl;
  }
  return groupUrl;
}

function getGroupNameFromUrl(groupUrl: string) {
  try {
    const parsed = new URL(groupUrl);
    const parts = parsed.pathname.split('/');
    const groupsIndex = parts.findIndex(part => part.toLowerCase() === 'groups');
    const slug = groupsIndex >= 0 ? parts[groupsIndex + 1] : '';
    return decodeURIComponent(slug || '').replace(/[-_.]+/g, ' ').trim() || parsed.hostname.replace(/^www\./, '');
  } catch {
    return groupUrl;
  }
}

function parseGroupUrls(rawUrls: string) {
  return [...new Set(rawUrls.split(/\r?\n/).map(normalizeGroupUrl).filter(Boolean))];
}

function isFacebookGroupUrl(groupUrl: string) {
  try {
    const parsed = new URL(groupUrl);
    const hostname = parsed.hostname.replace(/^www\./i, '').toLowerCase();
    const pathParts = parsed.pathname.toLowerCase().split('/').filter(Boolean);
    return hostname === 'facebook.com' && pathParts[0] === 'groups' && Boolean(pathParts[1]);
  } catch {
    return false;
  }
}

function privacyLabel(privacy?: string | null) {
  if (privacy === 'public') return 'Công khai';
  if (privacy === 'private') return 'Riêng tư';
  return 'Chưa rõ';
}

function privacyClassName(privacy?: string | null) {
  if (privacy === 'public') return 'badge-success';
  if (privacy === 'private') return 'badge-warning';
  return 'badge-info';
}

export function Groups() {
  const { data, loading, error, reload } = useAsync(api.groups, []);
  const { data: keywords, loading: keywordsLoading, error: keywordsError, reload: reloadKeywords } = useAsync(api.keywords, []);
  const [urls, setUrls] = useState('');
  const [keyword, setKeyword] = useState('');
  const [busy, setBusy] = useState(false);
  const [keywordBusy, setKeywordBusy] = useState(false);
  const [formError, setFormError] = useState('');
  const [keywordError, setKeywordError] = useState('');
  const [metadataRefreshed, setMetadataRefreshed] = useState(false);
  const groupUrls = useMemo(() => parseGroupUrls(urls), [urls]);

  useEffect(() => {
    if (loading || metadataRefreshed || !data?.length || !data.some(group => !group.privacy)) return;
    setMetadataRefreshed(true);
    api.refreshGroupMetadata().then(() => reload()).catch(() => undefined);
  }, [data, loading, metadataRefreshed, reload]);

  async function addGroups() {
    const invalidUrls = groupUrls.filter(groupUrl => !isFacebookGroupUrl(groupUrl));
    if (!groupUrls.length) return setFormError('Nhập ít nhất một URL group Facebook.');
    if (invalidUrls.length) return setFormError(`URL chưa đúng định dạng group Facebook:\n${invalidUrls.join('\n')}`);

    setBusy(true);
    setFormError('');
    try {
      const result = await api.createGroupsBatch(groupUrls.map(groupUrl => ({
        name: getGroupNameFromUrl(groupUrl),
        url: groupUrl,
        is_active: true,
      })));
      setUrls('');
      setMetadataRefreshed(false);
      await reload();
      if (result.skipped_urls.length) {
        setFormError(`Đã thêm ${result.created.length} group. Bỏ qua ${result.skipped_urls.length} group đã tồn tại.`);
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Không thể thêm group.');
    } finally {
      setBusy(false);
    }
  }

  async function addKeyword() {
    const value = keyword.trim();
    if (!value) return;
    setKeywordBusy(true);
    setKeywordError('');
    try {
      await api.createKeyword({ keyword: value, is_active: true });
      setKeyword('');
      await reloadKeywords();
    } catch (err) {
      setKeywordError(err instanceof Error ? err.message : 'Không thể thêm keyword.');
    } finally {
      setKeywordBusy(false);
    }
  }

  async function removeGroup(id: string) {
    if (!confirm('Xóa group này?')) return;
    setFormError('');
    try {
      await api.deleteGroup(id);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Không thể xóa group.');
    }
  }

  async function removeKeyword(id: string) {
    if (!confirm('Xóa keyword này?')) return;
    setKeywordError('');
    try {
      await api.deleteKeyword(id);
      await reloadKeywords();
    } catch (err) {
      setKeywordError(err instanceof Error ? err.message : 'Không thể xóa keyword.');
    }
  }

  function refreshAll() {
    setFormError('');
    setKeywordError('');
    void Promise.all([reload(), reloadKeywords()]).catch(err => {
      setFormError(err instanceof Error ? err.message : 'Không thể làm mới dữ liệu.');
    });
  }

  async function toggleKeyword(id: string, active: boolean) {
    setKeywordError('');
    try {
      await api.toggleKeyword(id, active);
      await reloadKeywords();
    } catch (err) {
      setKeywordError(err instanceof Error ? err.message : 'Không thể cập nhật keyword.');
    }
  }

  async function toggleGroup(id: string, active: boolean) {
    setFormError('');
    try {
      await api.updateGroup(id, { is_active: active });
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Không thể cập nhật group.');
    }
  }

  return (
    <div>
      <Topbar
        title="Facebook Groups"
        subtitle="Quản lý nguồn dữ liệu và chọn keyword cần theo dõi trong cùng một workspace."
        onRefresh={refreshAll}
      />

      <div className="grid gap-5 xl:grid-cols-[1.05fr_.95fr]">
        <section className="card-premium interactive-card p-5 md:p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#e1e8e6] text-[#102b2a]"><Link2 size={18} /></span>
            <div>
              <p className="eyebrow">Nguồn quét</p>
              <h2 className="mt-1 text-lg font-semibold tracking-[-0.025em]">Thêm Facebook Group</h2>
            </div>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-[1fr_auto]">
            <textarea
              className="input min-h-24 resize-y leading-6"
              wrap="off"
              placeholder="Dán URL group Facebook, mỗi dòng một group"
              value={urls}
              onChange={event => { setUrls(event.target.value); setFormError(''); }}
            />
            <button className="btn-primary md:self-stretch" disabled={busy || !groupUrls.length} onClick={addGroups}>
              <Plus size={17} />
              {busy ? 'Đang thêm...' : groupUrls.length > 1 ? `Thêm ${groupUrls.length} group` : 'Thêm group'}
            </button>
          </div>
          {formError && <div className="mt-3"><ErrorBox message={formError} /></div>}
        </section>

        <section className="card-premium interactive-card p-5 md:p-6">
          <div className="flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#d9eee9] text-[#16776f]"><Hash size={18} /></span>
            <div>
              <p className="eyebrow">Bộ lọc nội dung</p>
              <h2 className="mt-1 text-lg font-semibold tracking-[-0.025em]">Keyword theo dõi</h2>
              <p className="mt-1 text-xs leading-5 text-[#7d8784]">Click keyword để chọn hoặc bỏ chọn. Keyword sáng là keyword đang hoạt động.</p>
            </div>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-[1fr_auto]">
            <input
              className="input"
              placeholder="Nhập keyword mới"
              value={keyword}
              onChange={event => setKeyword(event.target.value)}
              onKeyDown={event => { if (event.key === 'Enter') void addKeyword(); }}
            />
            <button className="btn-primary" disabled={keywordBusy || !keyword.trim()} onClick={addKeyword}>
              <Plus size={17} />
              {keywordBusy ? 'Đang thêm...' : 'Thêm keyword'}
            </button>
          </div>

          <div className="mt-4">
            {keywordError && <div className="mb-3"><ErrorBox message={keywordError} /></div>}
            {keywordsLoading ? <Loading /> : keywordsError ? <ErrorBox message={keywordsError} /> : keywords?.length ? (
              <div className="flex flex-wrap gap-2.5">
                {keywords.map((item, index) => (
                  <div
                    key={item.id}
                    className="keyword-chip row-reveal"
                    data-selected={item.is_active}
                    style={{ '--row-index': index } as React.CSSProperties}
                  >
                    <button
                      className="flex items-center gap-2.5"
                      onClick={() => void toggleKeyword(item.id, !item.is_active)}
                      aria-pressed={item.is_active}
                    >
                      <span className="keyword-check"><Check size={14} strokeWidth={3} /></span>
                      <span className="text-sm font-semibold">{item.keyword}</span>
                    </button>
                    <button
                      onClick={() => removeKeyword(item.id)}
                      className="rounded-lg p-1.5 text-[#bd4b43] transition hover:bg-white/70"
                      aria-label={`Xóa keyword ${item.keyword}`}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                ))}
              </div>
            ) : <p className="rounded-xl bg-[#f7f8f5] p-4 text-xs text-[#7d8784]">Chưa có keyword. Khi không chọn keyword, hệ thống lấy tất cả bài viết mới.</p>}
          </div>
        </section>
      </div>

      <section className="card-premium mt-5 overflow-hidden">
        <div className="flex items-center justify-between border-b border-[#e4e7e1] px-5 py-4">
          <div>
            <p className="text-sm font-semibold">Danh sách group</p>
            <p className="mt-1 text-[11px] text-[#89918e]">{data?.length || 0} nguồn dữ liệu đã cấu hình</p>
          </div>
          <Users size={19} className="text-[#16776f]" />
        </div>
        {loading ? <div className="p-5"><Loading /></div> : error ? <div className="p-5"><ErrorBox message={error} /></div> : data?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-sm">
              <thead className="bg-[#fafbf8] text-[11px] uppercase tracking-[0.08em] text-[#7d8784]">
                <tr>
                  <th className="px-5 py-3 text-left">Group</th>
                  <th className="px-5 py-3 text-left">URL</th>
                  <th className="px-5 py-3 text-left">Trạng thái</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e8eae5]">
                {data.map((group, index) => (
                  <tr key={group.id} className="row-reveal transition-colors hover:bg-[#fafbf8]" style={{ '--row-index': index } as React.CSSProperties}>
                    <td className="px-5 py-4">
                      <p className="font-semibold text-[#253331]">{group.name}</p>
                      <span className={`badge mt-2 ${privacyClassName(group.privacy)}`}>{privacyLabel(group.privacy)}</span>
                    </td>
                    <td className="max-w-[520px] truncate px-5 py-4 text-xs text-[#66706d]">{group.url}</td>
                    <td className="px-5 py-4">
                      <button
                        onClick={() => void toggleGroup(group.id, !group.is_active)}
                        className={`badge transition hover:scale-105 ${group.is_active ? 'badge-success' : 'badge-info'}`}
                      >
                        {group.is_active ? 'Đang quét' : 'Tạm dừng'}
                      </button>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button className="btn-danger" onClick={() => removeGroup(group.id)} aria-label={`Xóa ${group.name}`}><Trash2 size={15} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="p-5"><Empty title="Chưa có group" desc="Thêm ít nhất một Facebook Group để bắt đầu quét." /></div>}
      </section>
    </div>
  );
}
