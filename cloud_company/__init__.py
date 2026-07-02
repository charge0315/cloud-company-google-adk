"""
Cloud-Company Google ADK パッケージ初期化。
モデル選択: ANTHROPIC_API_KEY が設定されている場合は Claude を優先、
未設定の場合は Gemini (gemini-2.5-flash) をデフォルトとする。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env を読み込む (プロジェクトルートから探索、なければ find_dotenv でフォールバック)
_root = Path(__file__).parent.parent
_env_file = _root / ".env"

if _env_file.exists():
    load_dotenv(_env_file, override=True)
else:
    # adk web のワーキングディレクトリが異なる場合のフォールバック
    from dotenv import find_dotenv
    _found = find_dotenv(usecwd=True)
    if _found:
        load_dotenv(_found, override=True)


# モデル選択ロジック
def get_default_model() -> str:
    """
    ANTHROPIC_API_KEY が設定されている場合は Claude Sonnet を返す。
    設定されていない場合は Gemini 2.5 Flash を返す。
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude-sonnet-4-5"
    return "gemini-2.5-flash"


DEFAULT_MODEL: str = get_default_model()

# 出力ディレクトリ
OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output")).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 既存 cloud-company パス (Manifesto 参照用)
CLOUD_COMPANY_PATH: Path = Path(
    os.getenv("CLOUD_COMPANY_PATH", "../cloud-company")
).resolve()
