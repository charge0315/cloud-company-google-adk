"""
Phase 3: キックオフ → 爆速環境構築・アサイン エージェント群。

Step 6: リソースアサイン (assign_agent)
Step 7: 環境構築 (infra_setup_agent)
Step 8: キックオフMTG (kickoff_meeting_agent) ← HITL で承認
→ kickoff_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document
from cloud_company.tools.manifesto_tools import load_manifesto
from cloud_company.tools.hitl_tools import confirm_kickoff

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 6: リソースアサイン
assign_agent = LlmAgent(
    name="assign_agent",
    model=DEFAULT_MODEL,
    description="FE/BE/インフラ/QAのメンバーを即座にアサインし、オンボーディングを完了する。",
    instruction=_load_prompt("phase3_assign.md"),
    tools=[load_manifesto, save_document],
    output_key="assign_result",
)

# Step 7: 環境構築
infra_setup_agent = LlmAgent(
    name="infra_setup_agent",
    model=DEFAULT_MODEL,
    description="2時間以内にGitHubリポジトリとCI/CDパイプライン、クラウド開発環境を構築して開発チームへ引き渡す。",
    instruction=_load_prompt("phase3_infra.md"),
    tools=[save_document],
    output_key="infra_result",
)

# Step 8: キックオフMTG (HITL)
kickoff_meeting_agent = LlmAgent(
    name="kickoff_meeting_agent",
    model=DEFAULT_MODEL,
    description=(
        "15分のフルリモートキックオフMTGを実施し、職人マシーン化を徹底する。"
        "MTG後にPMO（人間）のキックオフ承認を取得してから開発フェーズへ移行する。"
    ),
    instruction=_load_prompt("phase3_kickoff_meeting.md"),
    tools=[confirm_kickoff, save_document],
    output_key="kickoff_result",
)

# Phase 3 SequentialAgent オーケストレーター
kickoff_phase = SequentialAgent(
    name="kickoff_phase",
    description=(
        "Phase 3: リソースアサイン → 環境構築 → キックオフMTG (HITL) を順次実行する。"
    ),
    sub_agents=[assign_agent, infra_setup_agent, kickoff_meeting_agent],
)
