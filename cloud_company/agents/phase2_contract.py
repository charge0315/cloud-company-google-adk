"""
Phase 2: 商談・スコープ定義 → 契約・仮払い エージェント群。

Step 4: スコープ定義 (scope_definition_agent)
Step 5: 仮払い完了確認 HITL (payment_gate_agent) ← Human-in-the-Loop
→ contract_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document
from cloud_company.tools.manifesto_tools import load_manifesto
from cloud_company.tools.hitl_tools import confirm_payment_received

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 4: スコープ定義・合意
scope_definition_agent = LlmAgent(
    name="scope_definition_agent",
    model=DEFAULT_MODEL,
    description=(
        "スコープ内機能とスコープ外除外事項を明記した合意書を作成し、"
        "案件規模に応じたテーラリング判定を行う。"
    ),
    instruction=_load_prompt("phase2_scope.md"),
    tools=[load_manifesto, save_document],
    output_key="scope_result",
)

# Step 5: 仮払い完了確認 (HITL)
payment_gate_agent = LlmAgent(
    name="payment_gate_agent",
    model=DEFAULT_MODEL,
    description=(
        "仮払い完了の確認を Human-in-the-Loop で実施する。"
        "人間の承認がなければ次フェーズには進まない。"
    ),
    instruction=_load_prompt("phase2_payment_gate.md"),
    tools=[confirm_payment_received, save_document],
    output_key="payment_gate_result",
)

# Phase 2 SequentialAgent オーケストレーター
contract_phase = SequentialAgent(
    name="contract_phase",
    description=(
        "Phase 2: スコープ定義合意 → 仮払い完了確認 (HITL) を順次実行する。"
        "仮払い確認は人間の承認が必須。"
    ),
    sub_agents=[scope_definition_agent, payment_gate_agent],
)
