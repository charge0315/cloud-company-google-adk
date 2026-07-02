"""
Phase 1: 案件発掘・スクリーニング → 秒速提案 エージェント群。

Step 1: 案件スクリーニング (screening_agent)
Step 2: テクニカルアセスメント (assessment_agent)
Step 3: 秒速カスタマイズ提案 (proposal_agent)
→ bidding_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import create_project_folder, save_document
from cloud_company.tools.manifesto_tools import load_manifesto
from cloud_company.tools.review_tools import review_gate

# プロンプトを外部ファイルから読み込む
_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    """指定プロンプトファイルを読み込む。"""
    filepath = _prompts_dir / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return f"# {filename} プロンプトが見つかりません。"


# Step 1: 案件スクリーニング
screening_agent = LlmAgent(
    name="screening_agent",
    model=DEFAULT_MODEL,
    description="クラウドワークスの案件をスクリーニングし、受注すべき優良案件を選定する。",
    instruction=_load_prompt("phase1_screening.md"),
    tools=[load_manifesto, save_document, review_gate],
    output_key="screening_result",
)

# Step 2: テクニカルアセスメント
assessment_agent = LlmAgent(
    name="assessment_agent",
    model=DEFAULT_MODEL,
    description="スクリーニングされた案件に対して技術的実現可否と概算見積を30分以内に算出する。",
    instruction=_load_prompt("phase1_assessment.md"),
    tools=[load_manifesto, create_project_folder, save_document, review_gate],
    output_key="assessment_result",
)

# Step 3: 秒速カスタマイズ提案
proposal_agent = LlmAgent(
    name="proposal_agent",
    model=DEFAULT_MODEL,
    description="アセスメント結果を受けて掲載15分以内にコピペ臭ゼロの高精度提案メッセージを生成する。",
    instruction=_load_prompt("phase1_proposal.md"),
    tools=[save_document, review_gate],
    output_key="proposal_result",
)

# Phase 1 SequentialAgent オーケストレーター
bidding_phase = SequentialAgent(
    name="bidding_phase",
    description=(
        "Phase 1: 案件発掘・スクリーニング → テクニカルアセスメント → 秒速提案の3ステップを順次実行する。"
    ),
    sub_agents=[screening_agent, assessment_agent, proposal_agent],
)
