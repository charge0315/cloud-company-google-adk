"""
Phase 4: 画面案・設計・実装 → 独立QAテスト エージェント群。

Step 9-1: UIモック・顧客コンセンサス (ui_mock_agent)
Step 9-2〜9-4: FE設計・BE設計・FE実装 (design_dev_parallel ← ParallelAgent)
  ├── screen_detail_agent (FE詳細設計)
  ├── backend_design_agent (BE詳細設計)
  └── frontend_impl_agent (FE実装)
Step 10: 独立QAテスト (qa_agent)
→ development_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document
from cloud_company.tools.manifesto_tools import load_manifesto
from cloud_company.tools.review_tools import review_gate

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 9-1: UIモック・顧客コンセンサス
ui_mock_agent = LlmAgent(
    name="ui_mock_agent",
    model=DEFAULT_MODEL,
    description="主要画面のワイヤーフレームを作成し、クライアントコンセンサスを獲得する。",
    instruction=_load_prompt("phase4_ui_mock.md"),
    tools=[save_document],
    output_key="ui_mock_result",
)

# Step 9-2: FE詳細設計 (ParallelAgent の1つ)
screen_detail_agent = LlmAgent(
    name="screen_detail_agent",
    model=DEFAULT_MODEL,
    description="コンポーネント構造・状態遷移・バリデーションを定義した画面詳細設計書を作成する。",
    instruction=_load_prompt("phase4_screen_detail.md"),
    tools=[save_document],
    output_key="screen_detail_result",
)

# Step 9-3: BE詳細設計 (ParallelAgent の1つ)
backend_design_agent = LlmAgent(
    name="backend_design_agent",
    model=DEFAULT_MODEL,
    description="DB設計（テーブル定義・リレーション）とAPI仕様書（OpenAPI 3.0形式）を策定する。",
    instruction=_load_prompt("phase4_backend_design.md"),
    tools=[load_manifesto, save_document],
    output_key="backend_design_result",
)

# Step 9-4: FE実装 (ParallelAgent の1つ)
frontend_impl_agent = LlmAgent(
    name="frontend_impl_agent",
    model=DEFAULT_MODEL,
    description="画面詳細設計とAPI仕様に基づきUI実装・APIクライアント連携・状態管理ロジックを実装する。",
    instruction=_load_prompt("phase4_frontend_impl.md"),
    tools=[save_document],
    output_key="frontend_impl_result",
)

# Step 9-2〜9-4: 並列設計・実装フェーズ
# FE設計・BE設計・FE実装は互いに独立して並列実行可能
design_dev_parallel = ParallelAgent(
    name="design_dev_parallel",
    description=(
        "Step 9-2〜9-4: FE詳細設計・BE詳細設計・FE実装を並列実行する。"
        "3タスクは互いに独立しているため同時実行でコストと時間を削減する。"
    ),
    sub_agents=[screen_detail_agent, backend_design_agent, frontend_impl_agent],
)

# Step 10: 独立QAテスト
qa_agent = LlmAgent(
    name="qa_agent",
    model=DEFAULT_MODEL,
    description=(
        "仕様の裏をかくバグ検知シナリオを設計し、異常系・限界値・カオステストを実行する。"
        "全バグ修正・再テストパスまで納品フェーズへの移行をロックする。"
    ),
    instruction=_load_prompt("phase4_qa.md"),
    tools=[review_gate, save_document],
    output_key="qa_result",
)

# Phase 4 SequentialAgent オーケストレーター
development_phase = SequentialAgent(
    name="development_phase",
    description=(
        "Phase 4: UIモック → 並列設計・実装 (ParallelAgent) → QAテスト を順次実行する。"
        "設計・実装フェーズは並列化によりリードタイムを短縮する。"
    ),
    sub_agents=[ui_mock_agent, design_dev_parallel, qa_agent],
)
