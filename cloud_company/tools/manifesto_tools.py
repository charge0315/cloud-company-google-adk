"""
Manifesto 読み込みツール。
既存の cloud-company/.agents/skills/ 配下の Manifesto/Skillファイルを
エージェントの参照情報として読み込む。
"""

from pathlib import Path
from cloud_company import CLOUD_COMPANY_PATH

# Manifesto ファイルのマッピング（エージェント名 -> ファイル名）
_MANIFESTO_MAP: dict[str, str] = {
    "pmo": "pmo_department_manifesto.md",
    "bidding": "bidding_department_manifesto.md",
    "frontend": "frontend_department_manifesto.md",
    "backend": "backend_department_manifesto.md",
    "qa": "qa_department_manifesto.md",
    "sre_cs": "sre_cs_department_manifesto.md",
    "legal_finance": "legal_finance_department_manifesto.md",
    "hr_recruitment": "hr_recruitment_department_manifesto.md",
    "sales_cw": "sales_cw_department_manifesto.md",
    "pm": "pm_department_manifesto.md",
    "cm": "cm_department_manifesto.md",
}

_LEADER_MAP: dict[str, str] = {
    "pmo_leader": "project-management-office-leader.md",
    "bidding_leader": "proposal-bidding-team-leader.md",
    "frontend_leader": "frontend-engineering-leader.md",
    "backend_leader": "backend-engineering-leader.md",
    "infra_leader": "infrastructure-cloud-leader.md",
    "qa_leader": "06-qa-leader.md",
    "cw_account_leader": "cw-account-management-leader.md",
    "legal_finance_leader": "legal-finance-leader.md",
    "hr_leader": "hr-recruitment-leader.md",
    "sre_cs_leader": "sre-customer-success-leader.md",
    "technical_expert": "technical-expert-agent.md",
}


def load_manifesto(department: str) -> dict[str, str]:
    """
    指定部署のManifesto（行動憲章）を読み込んで返す。

    Args:
        department: 部署キー (例: "pmo", "frontend", "bidding_leader" 等)

    Returns:
        Manifesto の内容を含む辞書。
    """
    skills_dir = CLOUD_COMPANY_PATH / ".agents" / "skills"

    # Manifesto か Leader ファイルを探す
    filename = _MANIFESTO_MAP.get(department) or _LEADER_MAP.get(department)

    if filename is None:
        return {
            "error": f"Unknown department: '{department}'. "
            f"Valid keys: {list(_MANIFESTO_MAP) + list(_LEADER_MAP)}"
        }

    filepath = skills_dir / filename

    if not filepath.exists():
        return {
            "error": f"Manifesto file not found at: {filepath}. "
            "Ensure CLOUD_COMPANY_PATH is set correctly in .env"
        }

    content = filepath.read_text(encoding="utf-8")
    return {
        "status": "ok",
        "department": department,
        "filename": filename,
        "content": content[:4000],  # コンテキスト節約のため先頭 4000 文字
    }


def load_workflow_reference() -> dict[str, str]:
    """
    company-workflow.md を読み込んで全フェーズのワークフロー仕様を返す。

    Returns:
        ワークフロー仕様テキストを含む辞書。
    """
    workflow_file = CLOUD_COMPANY_PATH / "company-workflow.md"

    if not workflow_file.exists():
        return {
            "error": f"Workflow file not found at: {workflow_file}. "
            "Ensure CLOUD_COMPANY_PATH is set correctly in .env"
        }

    content = workflow_file.read_text(encoding="utf-8")
    return {
        "status": "ok",
        "content": content[:6000],  # 先頭 6000 文字
    }
