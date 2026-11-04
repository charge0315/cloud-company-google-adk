"""
ADK セッションDBから実行済みエージェント一覧を抽出するスクリプト。
"""
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "cloud_company" / ".adk" / "session.db"


def main() -> None:
    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}")
        return

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    # テーブル一覧
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    print(f"Tables: {tables}\n")

    # セッション一覧
    sessions = con.execute("SELECT * FROM sessions").fetchall() if "sessions" in tables else []
    print(f"Sessions ({len(sessions)}):")
    for s in sessions:
        d = dict(s)
        print(f"  id={d.get('id','?')} user={d.get('user_id','?')}")

    # イベント/メッセージからエージェント実行履歴を抽出
    agent_runs: dict[str, set[str]] = defaultdict(set)  # agent_name -> set of session_ids

    for tbl in ("events", "event", "messages", "message"):
        if tbl not in tables:
            continue
        rows = con.execute(f"SELECT * FROM {tbl}").fetchall()
        print(f"\n{tbl} table: {len(rows)} rows")
        for row in rows:
            d = dict(row)
            # author / agent フィールドを探す
            agent = d.get("author") or d.get("agent_name") or d.get("author_name")
            session_id = d.get("session_id") or d.get("id", "")[:8]
            if agent and agent not in ("user", "USER", None):
                agent_runs[agent].add(str(session_id)[:8])

            # content の JSON を掘り下げる
            for field in ("content", "data", "payload"):
                raw = d.get(field)
                if not raw:
                    continue
                try:
                    obj = json.loads(raw) if isinstance(raw, str) else raw
                    # ADK event 構造: {"author": "agent_name", ...}
                    a = obj.get("author") if isinstance(obj, dict) else None
                    if a and a not in ("user", "USER", None):
                        agent_runs[a].add(str(session_id)[:8])
                except Exception:
                    pass

    # 全エージェント定義
    ALL_AGENTS = [
        # Phase 1
        "screening_agent", "assessment_agent", "proposal_agent",
        # Phase 2
        "scope_definition_agent", "payment_gate_agent",
        # Phase 3
        "assign_agent", "infra_setup_agent", "kickoff_meeting_agent",
        # Phase 4
        "ui_mock_agent",
        "screen_detail_agent", "backend_design_agent", "frontend_impl_agent",
        "qa_agent",
        # Phase 5
        "delivery_package_agent", "review_gate_agent",
        "formal_delivery_agent", "cs_followup_agent",
        # Phase 6
        "incident_analysis_agent", "manifesto_update_agent", "skill_gap_agent",
        # Phase 7
        "tech_blog_agent", "package_sales_agent",
        # Orchestrators
        "cloud_company_orchestrator",
        "bidding_phase", "contract_phase", "kickoff_phase",
        "development_phase", "design_dev_parallel",
        "delivery_phase", "retrospective_phase", "marketing_phase",
    ]

    print("\n" + "=" * 60)
    print("エージェント稼働状況")
    print("=" * 60)
    ran = set(agent_runs.keys())
    for agent in ALL_AGENTS:
        status = "[RAN]  " if agent in ran else "[ -- ] "
        sessions_str = ", ".join(sorted(agent_runs[agent])) if agent in ran else ""
        print(f"  {status} {agent:<35} {sessions_str}")

    unknown = ran - set(ALL_AGENTS)
    if unknown:
        print(f"\n[INFO] 定義外のエージェント: {unknown}")

    ran_count = len([a for a in ALL_AGENTS if a in ran])
    total = len(ALL_AGENTS)
    print(f"\n合計: {ran_count}/{total} エージェントが稼働")
    con.close()


if __name__ == "__main__":
    main()
