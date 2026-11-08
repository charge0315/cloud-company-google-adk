"""
Cloud-Company ADK ワークフロー実行スクリプト。

使用方法:
  # 全フェーズ実行
  python scripts/run_workflow.py --project my-salon-saas --reqs "【案件名】..."

  # 特定フェーズのみ実行
  python scripts/run_workflow.py --project my-project --phase 1

  # インタラクティブモード (adk web に誘導)
  python scripts/run_workflow.py --web

  # ドライランモード (APIキー不要)
  python scripts/run_workflow.py --dry-run --project test-project --reqs "テスト案件"
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv(_project_root / ".env")

# API キーは資格情報マネージャーから読む（cloud_company/keyring_env.py）。下の _check_api_key より前に呼ぶ。
from cloud_company.keyring_env import load_keyring_secrets  # noqa: E402

load_keyring_secrets()


def _check_api_key() -> str:
    """利用可能な API キーを確認し、使用するモデルを返す。"""
    if os.getenv("ANTHROPIC_API_KEY"):
        print("[OK] ANTHROPIC_API_KEY を検出。Claude を優先使用します。")
        return "claude-sonnet-4-5"
    if os.getenv("GEMINI_API_KEY"):
        print("[OK] GEMINI_API_KEY を検出。Gemini 2.0 Flash を使用します。")
        return "gemini-2.0-flash"
    return ""


def run_web_ui() -> None:
    """adk web を起動するための案内を表示する。"""
    print("\n" + "=" * 60)
    print("[WEB] ADK Web UI を起動するには以下のコマンドを実行してください:")
    print("=" * 60)
    print(f"\n  adk web {_project_root / 'cloud_company'}")
    print("\nブラウザで http://localhost:8000 を開いてください。")
    print("=" * 60 + "\n")


def run_dry_run(project_name: str, requirements: str) -> None:
    """ドライランモード: APIキー不要で構造を確認する。"""
    from cloud_company.tools.project_tools import create_project_folder

    print("[DRY-RUN] Cloud-Company ADK Workflow (API key not required)")
    print(f"  Project: {project_name}")
    print(f"  Requirements (first 200 chars):\n{requirements[:200]}...")

    result = create_project_folder(project_name)
    print(f"\n[OK] Project folder created:")
    print(f"  Path: {result['project_path']}")
    print(f"  Subdirs: {result['subdirs']}")

    from cloud_company.agent import root_agent

    print(f"\n[OK] ADK Agent setup:")
    print(f"  Root agent: {root_agent.name}")
    print(f"  Sub-agent count: {len(root_agent.sub_agents)}")
    for phase_agent in root_agent.sub_agents:
        sub_count = len(phase_agent.sub_agents) if hasattr(phase_agent, "sub_agents") else 0
        print(f"    - {phase_agent.name} ({sub_count} sub-agents)")

    print("\n[OK] Dry run complete. An API key is required for actual execution.")


async def run_full_workflow(project_name: str, requirements: str) -> None:
    """ADK を使用してフルワークフローを実行する。"""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part

    from cloud_company.agent import root_agent

    print("\n" + "=" * 60)
    print("[START] Cloud-Company ADK ワークフロー開始")
    print("=" * 60)
    print(f"プロジェクト名: {project_name}")

    # セッションセットアップ
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="cloud_company",
        user_id="operator",
        session_id=f"session-{project_name}",
    )

    runner = Runner(
        agent=root_agent,
        app_name="cloud_company",
        session_service=session_service,
    )

    # 初期メッセージ
    initial_message = Content(
        role="user",
        parts=[
            Part(
                text=(
                    f"【プロジェクト名】{project_name}\n\n"
                    f"【案件要件】\n{requirements}\n\n"
                    "上記の案件要件に基づいて、Cloud-Company の全ワークフロー（Phase 1〜7）を実行してください。"
                )
            )
        ],
    )

    print("\n[WAIT] ワークフローを実行中...\n")

    async for event in runner.run_async(
        user_id="operator",
        session_id=f"session-{project_name}",
        new_message=initial_message,
    ):
        if event.is_final_response():
            print("\n" + "=" * 60)
            print("[OK] ワークフロー完了")
            print("=" * 60)
            if event.content and event.content.parts:
                print(event.content.parts[0].text)


def main() -> None:
    """メインエントリーポイント。"""
    parser = argparse.ArgumentParser(
        description="Cloud-Company Google ADK ワークフロー実行スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project", type=str, help="プロジェクト名（ケバブケースに自動変換）")
    parser.add_argument("--reqs", type=str, help="案件要件テキスト")
    parser.add_argument("--web", action="store_true", help="adk web の起動案内を表示")
    parser.add_argument("--dry-run", action="store_true", help="ドライランモード（APIキー不要）")

    args = parser.parse_args()

    if args.web:
        run_web_ui()
        return

    if not args.project:
        parser.error("--project は必須です。")

    requirements = args.reqs or (
        "【案件名】美容室向けLINE予約管理システム開発\n"
        "【予算】30万〜50万円\n"
        "【要件】\n"
        "- LINE公式アカウントと連携した予約管理機能\n"
        "- スタッフごとのシフト登録および予約枠の自動調整\n"
        "- 顧客カルテ（履歴）管理機能\n"
        "- Next.js / Python での構築希望"
    )

    if args.dry_run:
        run_dry_run(args.project, requirements)
        return

    model = _check_api_key()
    if not model:
        print("[!]  APIキーが設定されていません。")
        print("   .env ファイルに ANTHROPIC_API_KEY または GEMINI_API_KEY を設定してください。")
        print("   ドライランモードには --dry-run オプションを使用してください。")
        sys.exit(1)

    asyncio.run(run_full_workflow(args.project, requirements))


if __name__ == "__main__":
    main()
