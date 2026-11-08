"""OS の資格情報ストア（Windows は資格情報マネージャー）から API キーを読み、プロセスの環境変数へ入れる。

Why: ANTHROPIC_API_KEY をユーザー環境変数に置くと、同じユーザーで動く全プロセス（Claude Code の CLI を含む）が
そのキーを拾ってしまう（2026-11-08 に残高切れのキーで定期タスクが全部止まった）。キーは資格情報マネージャーに
1 件だけ置き、使うスクリプトが起動時に自分で読む。保存先のサービス名 `myworkspace` は ALPHA FORGE などと共通。

このパッケージでは `.env` を `override=True` で読んだあとに呼ぶ（`.env` に `ANTHROPIC_API_KEY=` と空で
書かれていても上書きで消されないようにするため）。優先順は「`.env` に値があればそれ > 起動時の環境変数 >
資格情報ストア」。keyring が無い・保存先が無い環境では何もしない。
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable

logger = logging.getLogger(__name__)

KEYRING_SERVICE = "myworkspace"
DEFAULT_SECRET_NAMES: tuple[str, ...] = ("ANTHROPIC_API_KEY",)


def load_keyring_secrets(names: Iterable[str] = DEFAULT_SECRET_NAMES, service: str = KEYRING_SERVICE) -> list[str]:
    """資格情報ストアにある値を、まだ環境変数に無い名前だけ os.environ へ入れる。入れた名前の一覧を返す。"""
    try:
        import keyring
        from keyring.errors import KeyringError
    except ImportError:
        logger.info("keyring が入っていないため、資格情報ストアからの読み込みを飛ばします")
        return []

    loaded: list[str] = []
    for name in names:
        if os.environ.get(name):
            continue
        try:
            value = keyring.get_password(service, name)
        except KeyringError as exc:
            # 値は出さず、失敗の種類だけ残す。
            logger.warning("資格情報ストアから %s を読めませんでした（%s）", name, type(exc).__name__)
            continue
        if value:
            os.environ[name] = value
            loaded.append(name)
    return loaded
