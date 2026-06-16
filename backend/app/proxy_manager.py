# backend/app/proxy_manager.py
from __future__ import annotations

import random
from typing import List, Optional

import requests


class ProxyManager:
    """Quản lý danh sách proxy: xoay vòng, random và kiểm tra hoạt động."""

    def __init__(self, proxy_list: Optional[List[str]] = None) -> None:
        self.proxy_list: List[str] = [p for p in (proxy_list or []) if p.strip()]
        self.current_index: int = 0

    # ------------------------------------------------------------------
    def add_proxy(self, proxy: str) -> None:
        self.proxy_list.append(proxy.strip())

    def get_next_proxy(self) -> Optional[str]:
        """Trả về proxy theo vòng tròn (round-robin)."""
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_index % len(self.proxy_list)]
        self.current_index += 1
        return proxy

    def get_random_proxy(self) -> Optional[str]:
        """Trả về proxy ngẫu nhiên từ danh sách."""
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)

    def test_proxy(self, proxy: str, timeout: int = 5) -> bool:
        """Kiểm tra proxy có hoạt động không."""
        try:
            proxies = {"http": proxy, "https": proxy}
            r = requests.get("https://api.ipify.org", proxies=proxies, timeout=timeout)
            return r.status_code == 200
        except Exception:
            return False

    def get_working_proxy(self) -> Optional[str]:
        """Trả về proxy đầu tiên hoạt động được."""
        for proxy in self.proxy_list:
            if self.test_proxy(proxy):
                return proxy
        return None
