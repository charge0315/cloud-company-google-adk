"""
Phase 7: インバウンド技術マーケティング & SaaS・サブスク展開（LTV最大化）エージェント群。

Step 18: 技術ブログ自動公開 (tech_blog_agent)
Step 19: SaaS化・準委任サブスク移行提案 (package_sales_agent)
→ marketing_phase (SequentialAgent) で順次実行
"""

from pathlib import Path
from google.adk.agents import LlmAgent, SequentialAgent

from cloud_company import DEFAULT_MODEL
from cloud_company.tools.project_tools import save_document, read_document

_prompts_dir = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    filepath = _prompts_dir / filename
    return filepath.read_text(encoding="utf-8") if filepath.exists() else f"# {filename} not found"


# Step 18: 技術ブログ自動公開
tech_blog_agent = LlmAgent(
    name="tech_blog_agent",
    model=DEFAULT_MODEL,
    description=(
        "プロジェクトで得た技術的知見を Qiita 記事原稿として自動生成する。"
        "インバウンドリード獲得によるクラウドワークス手数料ゼロ化・直接取引促進を目的とする。"
    ),
    instruction=_load_prompt("phase7_tech_blog.md"),
    tools=[read_document, save_document],
    output_key="tech_blog_result",
)

# Step 19: SaaS化・準委任サブスク移行提案
package_sales_agent = LlmAgent(
    name="package_sales_agent",
    model=DEFAULT_MODEL,
    description=(
        "請負で納品した成果物のホワイトラベルSaaS化と、"
        "クライアントへの準委任開発サブスクリプション移行提案を作成する。"
        "永続的なストックキャッシュフローへの転換によるLTV最大化を実現する。"
    ),
    instruction=_load_prompt("phase7_package_sales.md"),
    tools=[read_document, save_document],
    output_key="package_sales_result",
)

# Phase 7 SequentialAgent オーケストレーター
marketing_phase = SequentialAgent(
    name="marketing_phase",
    description=(
        "Phase 7: 技術ブログ原稿生成 → SaaS化・サブスク移行提案を順次実行する。"
        "LTV最大化によりプロジェクト単体の売上を超える継続的収益を実現する。"
    ),
    sub_agents=[tech_blog_agent, package_sales_agent],
)
