"""
プロジェクトフォルダ管理ツール。
cloud-company の規律に従い、ケバブケースのプロジェクトフォルダを
OUTPUT_DIR 配下に作成し、フェーズ別にドキュメントを保存・読込みする。
"""

import re
from pathlib import Path
from datetime import datetime

import cloud_company as _cc


def _get_output_dir() -> Path:
    """OUTPUT_DIR を動的に取得する（テスト時の差し替えに対応）。"""
    return _cc.OUTPUT_DIR


def _kebab_safe(name: str) -> str:
    """文字列をケバブケース（半角小文字英数字・ハイフン区切り）に変換する。"""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def create_project_folder(project_name: str) -> dict[str, str]:
    """
    プロジェクト専用フォルダをケバブケースで作成する。
    フェーズ別サブフォルダ (phase-2 〜 phase-5, phase-6, phase-7, incidents) も同時に生成する。

    Args:
        project_name: プロジェクト名（日本語・英語どちらでも可。ケバブケースに自動変換）

    Returns:
        作成したフォルダのパス情報を含む辞書。
    """
    safe_name = _kebab_safe(project_name)
    project_dir = _get_output_dir() / safe_name

    subdirs = [
        "phase-2-contract",
        "phase-3-kickoff",
        "phase-4-design-development",
        "phase-5-delivery",
        "phase-6-retrospective",
        "phase-7-marketing",
        "incidents",
        "reports",
    ]
    for sub in subdirs:
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    return {
        "status": "created",
        "project_name": safe_name,
        "project_path": str(project_dir),
        "subdirs": subdirs,
    }


def save_document(
    project_name: str,
    phase: str,
    filename: str,
    content: str,
) -> dict[str, str]:
    """
    指定フェーズのフォルダにMarkdownドキュメントを保存する。

    Args:
        project_name: プロジェクト名（ケバブケース）
        phase: フェーズ名 (例: "phase-4-design-development")
        filename: ファイル名 (例: "scope-definition.md")
        content: 保存するMarkdownコンテンツ

    Returns:
        保存結果を含む辞書。
    """
    safe_name = _kebab_safe(project_name)
    project_dir = _get_output_dir() / safe_name / phase
    project_dir.mkdir(parents=True, exist_ok=True)

    filepath = project_dir / filename
    filepath.write_text(content, encoding="utf-8")

    return {
        "status": "saved",
        "path": str(filepath),
        "bytes": str(len(content.encode("utf-8"))),
    }


def read_document(
    project_name: str,
    phase: str,
    filename: str,
) -> dict[str, str]:
    """
    指定フェーズのフォルダからMarkdownドキュメントを読み込む。

    Args:
        project_name: プロジェクト名（ケバブケース）
        phase: フェーズ名
        filename: ファイル名

    Returns:
        ファイル内容を含む辞書。見つからない場合は error キーを返す。
    """
    safe_name = _kebab_safe(project_name)
    filepath = _get_output_dir() / safe_name / phase / filename

    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    return {
        "status": "ok",
        "path": str(filepath),
        "content": filepath.read_text(encoding="utf-8"),
    }


def list_project_files(project_name: str) -> dict[str, list[str]]:
    """
    プロジェクトフォルダ内の全ファイル一覧を返す。

    Args:
        project_name: プロジェクト名（ケバブケース）

    Returns:
        フェーズごとのファイルリストを含む辞書。
    """
    safe_name = _kebab_safe(project_name)
    project_dir = _get_output_dir() / safe_name

    if not project_dir.exists():
        return {"error": f"Project not found: {project_dir}"}

    result: dict[str, list[str]] = {}
    for phase_dir in sorted(project_dir.iterdir()):
        if phase_dir.is_dir():
            result[phase_dir.name] = [
                f.name for f in sorted(phase_dir.iterdir()) if f.is_file()
            ]
    return result


def save_build_log_entry(
    project_name: str,
    phase: str,
    agent_name: str,
    summary: str,
) -> dict[str, str]:
    """
    プロジェクトビルドログ (docs/project-build-log.md) にエントリを追記する。
    Phase 6 の振り返り処理で使用される。

    Args:
        project_name: プロジェクト名
        phase: フェーズ名
        agent_name: ログを記録するエージェント名
        summary: ログ内容のサマリ

    Returns:
        保存結果を含む辞書。
    """
    safe_name = _kebab_safe(project_name)
    log_dir = _get_output_dir() / safe_name / "docs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "project-build-log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{timestamp}] [{phase}] {agent_name}\n{summary}\n"

    with log_file.open("a", encoding="utf-8") as f:
        f.write(entry)

    return {"status": "logged", "path": str(log_file)}
