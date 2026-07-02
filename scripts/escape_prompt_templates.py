"""
ADK の instruction テンプレートエンジンが {変数名} 形式の記述を
コンテキスト変数として解釈しようとするため、プロンプトMD内の
{...} をエスケープ（{{...}}）に一括変換するスクリプト。

対象: cloud_company/prompts/*.md
除外: 既に {{ }} になっているもの、コードブロック外の正当な変数
"""

import re
from pathlib import Path


def escape_template_vars(text: str) -> str:
    """
    ADK テンプレートエンジンが誤解釈する {xxx} を {{xxx}} にエスケープする。
    既に {{ }} になっているものはスキップ。
    """
    # 既に {{ になっている箇所はスキップしつつ、単独の { ... } をエスケープ
    # 手順: まず {{ }} を一時プレースホルダに退避 → { } を {{ }} に変換 → プレースホルダを戻す
    # プレースホルダ（ファイル中に絶対出現しない文字列）
    PLACEHOLDER_OPEN = "\x00DBLOPEN\x00"
    PLACEHOLDER_CLOSE = "\x00DBLCLOSE\x00"

    # Step1: 既存の {{ }} を退避
    text = text.replace("{{", PLACEHOLDER_OPEN)
    text = text.replace("}}", PLACEHOLDER_CLOSE)

    # Step2: 残った単独の { } をエスケープ
    text = text.replace("{", "{{")
    text = text.replace("}", "}}")

    # Step3: プレースホルダを戻す
    text = text.replace(PLACEHOLDER_OPEN, "{{")
    text = text.replace(PLACEHOLDER_CLOSE, "}}")

    return text


def process_file(filepath: Path) -> bool:
    original = filepath.read_text(encoding="utf-8")
    replaced = escape_template_vars(original)
    if original != replaced:
        filepath.write_text(replaced, encoding="utf-8")
        return True
    return False


def main() -> None:
    project_root = Path(__file__).parent.parent
    prompts_dir = project_root / "cloud_company" / "prompts"

    changed: list[Path] = []
    unchanged: list[Path] = []

    for filepath in sorted(prompts_dir.rglob("*.md")):
        if process_file(filepath):
            changed.append(filepath)
        else:
            unchanged.append(filepath)

    print(f"[DONE] Changed: {len(changed)}, Unchanged: {len(unchanged)}")
    for f in changed:
        print(f"  [ESCAPED] {f.name}")


if __name__ == "__main__":
    main()
