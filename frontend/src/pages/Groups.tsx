import { useEffect, useMemo, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
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
    const groupsIndex = parsed.pathname.toLowerCase().split('/').indexOf('groups');
    const groupSlug = groupsIndex >= 0 ? parsed.pathname.split('/')[groupsIndex + 1] : '';
    const decodedSlug = decodeURIComponent(groupSlug || '').replace(/[-_.]+/g, ' ').trim();
    return decodedSlug || parsed.hostname.replace(/^www\./, '');
  } catch {
    return groupUrl;
  }
}

function parseGroupUrls(rawUrls: string) {
  return rawUrls
    .split(/\r?\n/)
    .map(normalizeGroupUrl)
    .filter(Boolean);
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
  if (privacy === 'public') return 'Public';
  if (privacy === 'private') return 'Private';
  return 'Unknown';
}

function privacyClassName(privacy?: string | null) {
  if (privacy === 'public') return 'badge-success';
  if (privacy === 'private') return 'badge-warning';
  return 'badge-info';
}

export function Groups() {
  const { data, loading, error, reload } = useAsync(api.groups, []);
  const [urls, setUrls] = useState('');
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState('');
  const [metadataRefreshed, setMetadataRefreshed] = useState(false);
  const groupUrls = useMemo(() => parseGroupUrls(urls), [urls]);

  useEffect(() => {
    if (loading || metadataRefreshed || !data?.length) return;
    if (!data.some(group => !group.privacy)) return;

    setMetadataRefreshed(true);
    api.refreshGroupMetadata()
      .then(() => reload())
      .catch(() => undefined);
  }, [data, loading, metadataRefreshed, reload]);

  async function addGroups() {
    const invalidUrls = groupUrls.filter(groupUrl => !isFacebookGroupUrl(groupUrl));
    if (!groupUrls.length) {
      setFormError('Nhập ít nhất một URL group Facebook.');
      return;
    }
    if (invalidUrls.length) {
      setFormError(`URL chưa đúng định dạng group Facebook:\n${invalidUrls.join('\n')}`);
      return;
    }

    setBusy(true);
    setFormError('');
    try {
      for (const groupUrl of groupUrls) {
        await api.createGroup({
          name: getGroupNameFromUrl(groupUrl),
          url: groupUrl,
          is_active: true,
        });
      }
      setUrls('');
      setMetadataRefreshed(false);
      await reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Không thể thêm group.');
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    if (confirm('Xóa group này?')) {
      await api.deleteGroup(id);
      await reload();
    }
  }

  async function toggle(id: string, active: boolean) {
    await api.updateGroup(id, { is_active: active });
    await reload();
  }

  return (
    <div>
      <Topbar
        title="Facebook Groups"
        subtitle="Quản lý danh sách group cần quét. Chỉ thêm group em có quyền xem."
        onRefresh={reload}
      />

      <div className="card-premium p-4 mb-4">
        <h3 className="font-black mb-2">Thêm group mới</h3>
        <div className="grid md:grid-cols-[1fr_auto] gap-3 items-start">
          <textarea
            className="input min-h-14 resize-y leading-6"
            placeholder="Dán URL group Facebook, mỗi dòng một group"
            value={urls}
            onChange={e => {
              setUrls(e.target.value);
              setFormError('');
            }}
          />
          <button className="btn-primary md:min-h-14" disabled={busy || !groupUrls.length} onClick={addGroups}>
            <Plus size={18} />
            {busy ? 'Đang thêm...' : groupUrls.length > 1 ? `Thêm ${groupUrls.length} group` : 'Thêm'}
          </button>
        </div>
        {formError && <div className="mt-3"><ErrorBox message={formError} /></div>}
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : data?.length ? (
        <div className="card-premium overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="text-left p-3">Group</th>
                <th className="text-left p-3">URL</th>
                <th className="text-left p-3">Status</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {data.map(g => (
                <tr key={g.id} className="border-t border-slate-100">
                  <td className="p-3">
                    <div className="font-bold">{g.name}</div>
                    <span className={`badge mt-2 ${privacyClassName(g.privacy)}`}>{privacyLabel(g.privacy)}</span>
                  </td>
                  <td className="p-3 text-slate-500 max-w-[520px] truncate">{g.url}</td>
                  <td className="p-3">
                    <button
                      onClick={() => toggle(g.id, !g.is_active)}
                      className={`badge ${g.is_active ? 'badge-success' : 'badge-danger'}`}
                    >
                      {g.is_active ? 'Active' : 'Off'}
                    </button>
                  </td>
                  <td className="p-3 text-right">
                    <button className="btn-danger" onClick={() => remove(g.id)}>
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Empty title="Chưa có group" desc="Thêm ít nhất một Facebook Group để bắt đầu quét." />
      )}
    </div>
  );
}
