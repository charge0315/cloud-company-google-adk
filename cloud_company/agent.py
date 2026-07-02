"""
Cloud-Company Google ADK ルートエージェント。

ADK エントリーポイント: `adk web` および `adk run` はこのファイルの
`root_agent` 変数を自動認識して使用する。

ワークフロー構成:
  cloud_company_orchestrator (SequentialAgent)
  ├── [Phase 1] bidding_phase       - 案件発掘・スクリーニング → 秒速提案
  ├── [Phase 2] contract_phase      - スコープ定義 → 仮払い確認 (HITL)
  ├── [Phase 3] kickoff_phase       - リソースアサイン → 環境構築 → キックオフ (HITL)
  ├── [Phase 4] development_phase   - UIモック → 並列設計・実装 → QA
  ├── [Phase 5] delivery_phase      - 納品 (HITL) → CS対応 → レビューゲート
  ├── [Phase 6] retrospective_phase - インシデント分析 → Manifesto更新 → スキルギャップ
  └── [Phase 7] marketing_phase     - 技術ブログ → SaaS化・サブスク提案

モデル選択:
  ANTHROPIC_API_KEY が設定されている場合: Claude を優先使用
  未設定の場合: Gemini 2.0 Flash をデフォルト使用
"""

from google.adk.agents import SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.agents.phase1_bidding import bidding_phase
from cloud_company.agents.phase2_contract import contract_phase
from cloud_company.agents.phase3_kickoff import kickoff_phase
from cloud_company.agents.phase4_development import development_phase
from cloud_company.agents.phase5_delivery import delivery_phase
from cloud_company.agents.phase6_retrospective import retrospective_phase
from cloud_company.agents.phase7_marketing import marketing_phase


# ─── ルートオーケストレーター ──────────────────────────────────────
# ADK は `root_agent` という名前の変数をエントリーポイントとして認識する
root_agent = SequentialAgent(
    name="cloud_company_orchestrator",
    description=(
        "Cloud-Company 全社ワークフローオーケストレーター。\n"
        "クラウドソーシング案件の受注から納品・振り返り・LTV最大化まで、"
        "全7フェーズ・19ステップを自律的に連携して実行する。\n\n"
        f"使用モデル: {DEFAULT_MODEL}\n\n"
        "フェーズ構成:\n"
        "  Phase 1: 案件発掘・スクリーニング → 秒速提案\n"
        "  Phase 2: スコープ定義 → 仮払い確認 (HITL)\n"
        "  Phase 3: リソースアサイン → 環境構築 → キックオフ (HITL)\n"
        "  Phase 4: UIモック → 並列設計・実装 (ParallelAgent) → QA\n"
        "  Phase 5: 納品パッケージ (HITL) → 正式納品 → CS → レビューゲート\n"
        "  Phase 6: インシデント分析 → Manifesto自動更新 → スキルギャップ分析\n"
        "  Phase 7: 技術ブログ生成 → SaaS化・サブスク移行提案\n"
    ),
    sub_agents=[
        bidding_phase,
        contract_phase,
        kickoff_phase,
        development_phase,
        delivery_phase,
        retrospective_phase,
        marketing_phase,
    ],
)
