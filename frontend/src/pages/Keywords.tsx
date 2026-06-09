import { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { api } from '../lib/api';
import { useAsync } from '../lib/hooks';
import { Topbar } from '../components/Topbar';
import { Empty, ErrorBox, Loading } from '../components/State';

export function Keywords() {
  const { data, loading, error, reload } = useAsync(api.keywords, []);
  const [keyword, setKeyword] = useState('');

  async function add() {
    const value = keyword.trim();
    if (!value) return;

    await api.createKeyword({ keyword: value, is_active: true });
    setKeyword('');
    await reload();
  }

  async function remove(id: string) {
    if (confirm('Xóa keyword?')) {
      await api.deleteKeyword(id);
      await reload();
    }
  }

  async function toggle(id: string, active: boolean) {
    await api.toggleKeyword(id, active);
    await reload();
  }

  return (
    <div>
      <Topbar
        title="Keyword Filter"
        subtitle="Chỉ lưu/gửi alert những bài viết có chứa keyword. Nếu không có keyword active, backend sẽ lấy tất cả bài mới."
        onRefresh={reload}
      />

      <div className="card-premium p-5 mb-5">
        <div className="grid md:grid-cols-[1fr_auto] gap-3">
          <input
            className="input"
            placeholder="nhập key word"
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') void add();
            }}
          />
          <button className="btn-primary" disabled={!keyword.trim()} onClick={add}>
            <Plus size={18} />
            Thêm keyword
          </button>
        </div>
      </div>

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : data?.length ? (
        <div className="flex flex-wrap gap-3">
          {data.map(k => (
            <div key={k.id} className="card-premium px-4 py-3 flex items-center gap-3">
              <button
                onClick={() => toggle(k.id, !k.is_active)}
                className={`badge ${k.is_active ? 'badge-success' : 'badge-danger'}`}
              >
                {k.is_active ? 'ON' : 'OFF'}
              </button>
              <b>{k.keyword}</b>
              <button onClick={() => remove(k.id)} className="text-red-500 hover:bg-red-50 rounded-lg p-1">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <Empty title="Chưa có keyword" desc="Thêm keyword để lọc bài viết theo nhu cầu." />
      )}
    </div>
  );
}
