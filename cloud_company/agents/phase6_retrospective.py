"""
Phase 6: 振り返り・改善ループ（AgentOps Retrospective）エージェント群。

Step 15: フェーズ別インシデント分析 (incident_analysis_agent)
Step 16: 改善ルール生成・Manifesto自動更新 (manifesto_update_agent)
Step 17: スキルギャップ分析・ナレッジ共有 (skill_gap_agent)
→ retrospective_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document, read_document
from cloud_company.tools.manifesto_tools import load_manifesto, load_workflow_reference
from cloud_company.tools.review_tools import review_gate

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 15: フェーズ別インシデント分析
incident_analysis_agent = LlmAgent(
    name="incident_analysis_agent",
    model=DEFAULT_MODEL,
    description=(
        "プロジェクトビルドログとインシデントファイルを収集・分析し、"
        "フェーズ別の問題点・根本原因・影響度を自動分析して振り返りレポートを生成する。"
    ),
    instruction=_load_prompt("phase6_incident_analysis.md"),
    tools=[read_document, save_document, review_gate],
    output_key="incident_analysis_result",
)

# Step 16: Manifesto 自動更新
manifesto_update_agent = LlmAgent(
    name="manifesto_update_agent",
    model=DEFAULT_MODEL,
    description=(
        "振り返り分析で特定された問題の再発防止ルールを生成し、"
        "各エージェントのManifesto（行動憲章）に自動追記する（AgentOpsループ）。"
    ),
    instruction=_load_prompt("phase6_manifesto_update.md"),
    tools=[load_manifesto, save_document, review_gate],
    output_key="manifesto_update_result",
)

# Step 17: スキルギャップ分析
skill_gap_agent = LlmAgent(
    name="skill_gap_agent",
    model=DEFAULT_MODEL,
    description=(
        "スキルギャップ分析をもとに習得が必要なスキル・知識を特定し、"
        "共有スキルファイルを更新して全エージェントへ展開する。"
    ),
    instruction=_load_prompt("phase6_skill_gap.md"),
    tools=[load_workflow_reference, save_document, review_gate],
    output_key="skill_gap_result",
)

# Phase 6 SequentialAgent オーケストレーター
retrospective_phase = SequentialAgent(
    name="retrospective_phase",
    description=(
        "Phase 6: インシデント分析 → Manifesto自動更新 → スキルギャップ分析 を順次実行する。"
        "AgentOpsループにより次回プロジェクトの品質を自己進化させる。"
    ),
    sub_agents=[incident_analysis_agent, manifesto_update_agent, skill_gap_agent],
)
