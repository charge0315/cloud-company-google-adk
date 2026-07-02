# 🤖 Cloud-Company Google ADK マルチエージェントシステム

[![Google ADK](https://img.shields.io/badge/Google_ADK-2.2+-blue)](https://adk.dev/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-11%20passed-brightgreen)](tests/)

**cloud-company-google-adk** は、クラウドソーシング案件の受注〜納品〜LTV最大化に至る**全7フェーズ・19ステップ**を、Google ADK (Agent Development Kit) を使用したマルチエージェントシステムとして実装したプロジェクトです。

既存の Dify 版 (`cloud-company/dify-reproduction/`) と並列で使用でき、ADK ならではの **コードファースト・グラフ型オーケストレーション** を体験できます。

---

## 🏗️ アーキテクチャ

```
cloud_company_orchestrator (SequentialAgent)
├── [Phase 1] bidding_phase (SequentialAgent)         ← 案件発掘・提案
│   ├── screening_agent (LlmAgent)                    - 案件スクリーニング
│   ├── assessment_agent (LlmAgent)                   - テクニカルアセスメント
│   └── proposal_agent (LlmAgent)                     - 秒速提案生成
├── [Phase 2] contract_phase (SequentialAgent)        ← 契約・仮払い
│   ├── scope_definition_agent (LlmAgent)             - スコープ定義
│   └── payment_gate_agent (LlmAgent) [HITL]          - 仮払い確認 ⚠️
├── [Phase 3] kickoff_phase (SequentialAgent)         ← キックオフ
│   ├── assign_agent (LlmAgent)                       - リソースアサイン
│   ├── infra_setup_agent (LlmAgent)                  - 環境構築
│   └── kickoff_meeting_agent (LlmAgent) [HITL]       - キックオフMTG ⚠️
├── [Phase 4] development_phase (SequentialAgent)     ← 設計・実装
│   ├── ui_mock_agent (LlmAgent)                      - UIモック
│   ├── design_dev_parallel (ParallelAgent)           - 並列設計・実装 🔀
│   │   ├── screen_detail_agent (LlmAgent)            - FE詳細設計
│   │   ├── backend_design_agent (LlmAgent)           - BE詳細設計
│   │   └── frontend_impl_agent (LlmAgent)            - FE実装
│   └── qa_agent (LlmAgent)                           - カオスQA
├── [Phase 5] delivery_phase (SequentialAgent)        ← 納品
│   ├── delivery_package_agent (LlmAgent) [HITL]      - 納品パッケージ ⚠️
│   ├── formal_delivery_agent (LlmAgent)              - 正式納品
│   ├── cs_followup_agent (LlmAgent)                  - CS対応
│   └── review_gate_agent (LlmAgent)                  - レビューゲート
├── [Phase 6] retrospective_phase (SequentialAgent)   ← 振り返り
│   ├── incident_analysis_agent (LlmAgent)            - インシデント分析
│   ├── manifesto_update_agent (LlmAgent)             - Manifesto更新
│   └── skill_gap_agent (LlmAgent)                    - スキルギャップ分析
└── [Phase 7] marketing_phase (SequentialAgent)       ← LTV最大化
    ├── tech_blog_agent (LlmAgent)                    - 技術ブログ生成
    └── package_sales_agent (LlmAgent)               - SaaS化・サブスク提案

⚠️ HITL = Human-in-the-Loop (人間の承認が必要なチェックポイント)
🔀 ParallelAgent = 同時並列実行でリードタイム短縮
```

---

## 🚀 クイックスタート

### 1. 必要環境
- Python 3.11+
- `google-adk >= 2.2.0`

### 2. セットアップ

```powershell
# 環境変数ファイルを作成
Copy-Item .env.example .env

# .env を編集してAPIキーを設定
# ANTHROPIC_API_KEY=sk-ant-... (Claude 優先)
# または
# GEMINI_API_KEY=AIza...       (Gemini フォールバック)
```

### 3. ドライランモード（APIキー不要）

```powershell
$env:PYTHONIOENCODING="utf-8"
py -3.11 scripts/run_workflow.py --dry-run --project my-salon-saas --reqs "LINE reservation system"
```

### 4. ADK Web UI で実行

```powershell
# ADK Web UI を起動（推奨）
adk web cloud_company/

# ブラウザで http://localhost:8000 を開く
```

### 5. CLI で実行（APIキー必要）

```powershell
$env:PYTHONIOENCODING="utf-8"
# Claude を優先使用
$env:ANTHROPIC_API_KEY="sk-ant-..."
py -3.11 scripts/run_workflow.py --project my-salon-saas --reqs "【案件名】美容室LINE予約..."

# Gemini を使用
$env:GEMINI_API_KEY="AIza..."
py -3.11 scripts/run_workflow.py --project my-project --reqs "..."
```

---

## 🧪 テスト実行

```powershell
# 単体テスト（11件）
py -3.11 -m pytest tests/test_tools.py -v -W ignore::DeprecationWarning

# ADK 評価テスト（フェーズ1）
adk eval cloud_company/ eval/test_bidding_phase.json
```

---

## 📁 ディレクトリ構成

```
cloud-company-google-adk/
├── cloud_company/           # メインパッケージ (ADK エントリーポイント)
│   ├── agent.py             # root_agent 定義（全7フェーズ結合）
│   ├── agents/              # フェーズ別エージェント実装
│   │   ├── phase1_bidding.py
│   │   ├── phase2_contract.py
│   │   ├── phase3_kickoff.py
│   │   ├── phase4_development.py  # ParallelAgent 含む
│   │   ├── phase5_delivery.py
│   │   ├── phase6_retrospective.py
│   │   └── phase7_marketing.py
│   ├── tools/               # FunctionTool 実装
│   │   ├── project_tools.py     # プロジェクトフォルダ管理
│   │   ├── manifesto_tools.py   # Manifesto 読み込み
│   │   ├── review_tools.py      # High/Medium/Low レビューゲート
│   │   └── hitl_tools.py        # Human-in-the-Loop
│   └── prompts/             # エージェント指示プロンプト（Markdown）
│       └── phase*_*.md      # 各ステップのプロンプト（21ファイル）
├── scripts/
│   └── run_workflow.py      # CLI 実行エントリーポイント
├── eval/                    # ADK 評価テストケース
├── tests/                   # pytest 単体テスト
├── output/                  # ワークフロー実行成果物（自動生成）
├── pyproject.toml
└── .env.example
```

---

## 🔑 モデル選択ポリシー

| 優先順位 | 条件 | 使用モデル |
|---------|------|-----------|
| 1 | `ANTHROPIC_API_KEY` が設定されている | Claude Sonnet |
| 2 | `GEMINI_API_KEY` が設定されている | Gemini 2.0 Flash |

`cloud_company/__init__.py` の `get_default_model()` で自動選択されます。

---

## ⚠️ ADK バージョンノート

`google-adk 2.2.0` では `SequentialAgent` / `ParallelAgent` は **deprecated** です
（`Workflow` への移行が推奨されています）。
本プロジェクトでは現在これらを使用しており、`DeprecationWarning` が表示されますが、
機能的には完全に動作します。`Workflow` への移行は次バージョンで対応予定です。

---

## 📊 既存 cloud-company との関係

```
c:\Users\charg\myWorkspace\
├── cloud-company/                ← 既存（変更なし）
│   ├── dify-reproduction/        - Dify GUI ベース版
│   └── scripts/create_project.py - Claude API Python 版
└── cloud-company-google-adk/    ← このプロジェクト (Google ADK 版)
```
