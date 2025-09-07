import time
import asyncio
import threading
from typing import Optional, Any
import collections.abc


class ExpiringDict(collections.abc.MutableMapping):
    def __init__(self, expiration_time: int):
        self.data = {}
        self.expiration_time = expiration_time
        self.expiration_tasks = {}  # 非同期タスク管理
        self.expiration_timers = {}  # 同期タイマー管理
        self._loop = None

    def __getstate__(self):
        """
        pickle化する際に呼ばれるメソッド。
        保存すべき状態だけを含む辞書を返す。
        """
        return {
            'data': self.data,
            'expiration_time': self.expiration_time,
        }

    def __setstate__(self, state):
        """
        pickleから復元する際に呼ばれるメソッド。
        __getstate__で返した辞書を受け取り、オブジェクトの状態を復元する。
        """
        self.data = state['data']
        self.expiration_time = state['expiration_time']

        # タイマーやタスクに関連する変数を初期化する
        self.expiration_tasks = {}
        self.expiration_timers = {}
        self._loop = None

        # 復元されたデータすべてに対して、再度タイマーを設定し直す
        # 注意: 復元された時点から新しい有効期限がスタートする
        for key in list(self.data.keys()):
            self._set_expiration(key)

    def _get_or_create_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """実行中のループを取得、なければ新規作成"""
        try:
            # 実行中のループがあるか確認
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:
            # ループが実行中でない場合
            try:
                # 既存のループがあるか確認
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                return loop
            except RuntimeError:
                # 新しいループを作成
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop

    def _set_expiration_sync(self, key: str):
        """同期版の有効期限設定（daemon化）"""
        if key in self.expiration_timers:
            self.expiration_timers[key].cancel()

        def remove_key():
            if key in self.data:
                del self.data[key]
                print(f"Key '{key}' expired and removed at {time.time()}")
            if key in self.expiration_timers:
                del self.expiration_timers[key]

        timer = threading.Timer(self.expiration_time, remove_key)
        timer.daemon = True  # ← この1行だけ追加
        timer.start()
        self.expiration_timers[key] = timer

    async def _set_expiration_async(self, key: str):
        """非同期版の有効期限設定"""
        # 既存のタスクをキャンセル
        if key in self.expiration_tasks:
            self.expiration_tasks[key].cancel()

        # 新しいタスクを設定
        task = asyncio.create_task(self._remove_after_delay(key))
        self.expiration_tasks[key] = task

    async def _remove_after_delay(self, key: str):
        """指定されたキーを一定時間後に削除（非同期版）"""
        await asyncio.sleep(self.expiration_time)
        if key in self.data:
            del self.data[key]
            print(f"Key '{key}' expired and removed at {time.time()}")
        if key in self.expiration_tasks:
            del self.expiration_tasks[key]

    def _set_expiration(self, key: str):
        """自動判定で有効期限を設定"""
        try:
            # 実行中のループがあるかチェック
            loop = asyncio.get_running_loop()
            # ループが実行中なら非同期で処理
            asyncio.create_task(self._set_expiration_async(key))
        except RuntimeError:
            # ループが実行中でなければ同期で処理
            self._set_expiration_sync(key)

    def __setitem__(self, key: str, value: Any):
        """辞書風の値設定（同期・非同期自動判定）"""
        self.data[key] = value
        self._set_expiration(key)

    def __getitem__(self, key: str):
        """辞書風の値取得"""
        return self.data[key]

    def __delitem__(self, key: str):
        """辞書風の値削除"""
        if key in self.data:
            del self.data[key]
            # タイマー/タスクのクリーンアップ
            if key in self.expiration_timers:
                self.expiration_timers[key].cancel()
                del self.expiration_timers[key]
            if key in self.expiration_tasks:
                self.expiration_tasks[key].cancel()
                del self.expiration_tasks[key]

    def __iter__(self):
        """辞書のキーをイテレートするためのメソッド"""
        return iter(self.data)

    def __len__(self):
        """辞書の要素数を返すためのメソッド"""
        return len(self.data)

    def __contains__(self, key: str):
        return key in self.data

    def __repr__(self):
        return repr(self.data)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def values(self):
        return self.data.values()

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def clear(self):
        """全データとタスクをクリア"""
        self.data.clear()
        for timer in self.expiration_timers.values():
            timer.cancel()
        self.expiration_timers.clear()
        for task in self.expiration_tasks.values():
            task.cancel()
        self.expiration_tasks.clear()
