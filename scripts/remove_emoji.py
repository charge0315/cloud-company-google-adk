"""
絵文字をASCII代替テキストに一括置換するスクリプト。
cloud_company/ 配下の全 .py / .md ファイルを対象にする。
"""

import re
from pathlib import Path

# 絵文字 → ASCII 代替テキストのマッピング
EMOJI_MAP = {
    # 状態系
    "[OK]": "[OK]",
    "[NG]": "[NG]",
    "[!]": "[!]",
    "[!]": "[!]",
    "[HIGH]": "[HIGH]",
    "[MEDIUM]": "[MEDIUM]",
    "[PASS]": "[PASS]",
    "[LOCK]": "[LOCK]",
    "[STOP]": "[STOP]",
    # フェーズ・アイコン系
    "[START]": "[START]",
    "[WEB]": "[WEB]",
    "[SEARCH]": "[SEARCH]",
    "[DOC]": "[DOC]",
    "[REPORT]": "[REPORT]",
    "[DIR]": "[DIR]",
    "[PKG]": "[PKG]",
    "[MEMO]": "[MEMO]",
    "[TIP]": "[TIP]",
    "[GOAL]": "[GOAL]",
    "[KEY]": "[KEY]",
    "[FIX]": "[FIX]",
    "[BUILD]": "[BUILD]",
    "[BUILD]": "[BUILD]",
    "[MONEY]": "[MONEY]",
    "[AGENT]": "[AGENT]",
    "[WAIT]": "[WAIT]",
    "[DONE]": "[DONE]",
    # チェックボックス系
    "[x]": "[x]",
    "[ ]": "[ ]",
    # その他記号
    "[PARALLEL]": "[PARALLEL]",
    "[WORK]": "[WORK]",
    "[UP]": "[UP]",
    "[TEST]": "[TEST]",
    "[TOOL]": "[TOOL]",
    "[TOOL]": "[TOOL]",
}

# BMP外の絵文字（\U000xxxxx）も削除するパターン
SUPPLEMENTARY_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FFFF"   # Misc symbols, emoticons
    "\U00002600-\U000027BF"    # Misc symbols
    "\U0001F300-\U0001F9FF"    # More emoji
    "\U00002B00-\U00002BFF"    # Arrows etc
    "\U0000FE00-\U0000FE0F"    # Variation selectors
    "]",
    flags=re.UNICODE,
)


def replace_emoji(text: str) -> str:
    """テキスト中の絵文字をASCII代替テキストに置換する。"""
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    # マッピングに含まれない補助多言語面絵文字は除去
    text = SUPPLEMENTARY_EMOJI_RE.sub("", text)
    return text


def process_file(filepath: Path) -> bool:
    """ファイルを処理し、変更があれば上書き保存する。変更した場合Trueを返す。"""
    original = filepath.read_text(encoding="utf-8")
    replaced = replace_emoji(original)
    if original != replaced:
        filepath.write_text(replaced, encoding="utf-8")
        return True
    return False


def main() -> None:
    project_root = Path(__file__).parent.parent
    target_dirs = [
        project_root / "cloud_company",
        project_root / "scripts",
    ]

    changed: list[Path] = []
    unchanged: list[Path] = []

    for target_dir in target_dirs:
        for ext in ("*.py", "*.md"):
            for filepath in sorted(target_dir.rglob(ext)):
                if process_file(filepath):
                    changed.append(filepath)
                else:
                    unchanged.append(filepath)

    print(f"[DONE] Changed: {len(changed)} files, Unchanged: {len(unchanged)} files")
    for f in changed:
        print(f"  [CHANGED] {f.relative_to(project_root)}")


if __name__ == "__main__":
    main()
