"""
Phase 5: 正式納品 → 一発検収・売上確定・評価星5 エージェント群。

Step 11: 納品パッケージ作成 (delivery_package_agent)
Step 12: 正式納品 (formal_delivery_agent) ← HITL
Step 13: CS対応・アップセル (cs_followup_agent)
Step 14: レビューゲート (review_gate_agent)
→ delivery_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document
from cloud_company.tools.review_tools import review_gate
from cloud_company.tools.hitl_tools import confirm_delivery

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 11: 納品パッケージ作成
delivery_package_agent = LlmAgent(
    name="delivery_package_agent",
    model=DEFAULT_MODEL,
    description=(
        "デモ動画収録手順書・納品説明書・アップセル提案書を作成する。"
        "作成後に人間（PMO）の最終確認を HITL で取得する。"
    ),
    instruction=_load_prompt("phase5_delivery_package.md"),
    tools=[confirm_delivery, save_document],
    output_key="delivery_package_result",
)

# Step 12: 正式納品
formal_delivery_agent = LlmAgent(
    name="formal_delivery_agent",
    model=DEFAULT_MODEL,
    description=(
        "クラウドワークスの「納品する」ボタンをクリックするための"
        "正式納品メッセージと納品完了記録を生成する。"
    ),
    instruction=_load_prompt("phase5_formal_delivery.md"),
    tools=[save_document],
    output_key="formal_delivery_result",
)

# Step 13: 検収期間中CSフォロー・アップセル
cs_followup_agent = LlmAgent(
    name="cs_followup_agent",
    model=DEFAULT_MODEL,
    description=(
        "検収期間中のCS対応（15分以内即答・2時間修正デプロイ）と"
        "スコープ外追加要望の有償アップセル誘導を行う。"
    ),
    instruction=_load_prompt("phase5_cs_followup.md"),
    tools=[save_document],
    output_key="cs_followup_result",
)

# Step 14: 検収完了後レビューゲート
review_gate_agent = LlmAgent(
    name="review_gate_agent",
    model=DEFAULT_MODEL,
    description=(
        "検収完了後に全フェーズのレビュー指摘事項を評価し、"
        "High/Medium/Low の重要度で次フェーズ（Phase 6）への移行可否を判定する。"
    ),
    instruction=(
        "あなたは Cloud-Company の最終レビューゲート管理者です。\n"
        "全フェーズで発生した指摘事項を整理し、`review_gate` ツールを使って"
        "High/Medium/Low の重要度で評価してください。\n"
        "全てのHighレベル指摘が解消されていることを確認した後、"
        "Phase 6（振り返り）への移行を承認してください。"
    ),
    tools=[review_gate, save_document],
    output_key="review_gate_result",
)

# Phase 5 SequentialAgent オーケストレーター
delivery_phase = SequentialAgent(
    name="delivery_phase",
    description=(
        "Phase 5: 納品パッケージ作成 (HITL) → 正式納品 → CS対応 → レビューゲート を順次実行する。"
    ),
    sub_agents=[
        delivery_package_agent,
        formal_delivery_agent,
        cs_followup_agent,
        review_gate_agent,
    ],
)
