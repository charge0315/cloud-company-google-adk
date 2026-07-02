"""
レビューゲートツール。
cloud-company の「指摘重要度に応じた Review Gate」規律を実装する。
High / Medium / Low の3段階でレビュー結果を格付けし、次フェーズへの移行可否を判定する。
"""

from typing import Literal


ReviewLevel = Literal["High", "Medium", "Low"]


def review_gate(
    project_name: str,
    phase: str,
    reviewer: str,
    issues: list[dict[str, str]],
) -> dict[str, object]:
    """
    レビュー指摘事項を評価し、次フェーズへの移行可否を判定する。

    規律:
    - High（致命的）: 完全な修正と再レビューによる「PASS」が必須。
    - Medium（主要）: 修正エビデンス提出で「条件付きPASS」として次工程に進める。
    - Low（軽微）: チケット登録し即座に「PASS（スキップ）」として次工程に進める。

    Args:
        project_name: プロジェクト名
        phase: レビュー対象フェーズ名
        reviewer: レビュアー名
        issues: 指摘事項リスト。各要素は {"level": "High|Medium|Low", "description": str} の形式。

    Returns:
        判定結果を含む辞書。
        - "gate_status": "PASS" | "CONDITIONAL_PASS" | "BLOCKED"
        - "can_proceed": bool
        - "message": str
        - "high_issues": list  (要修正の致命的指摘)
        - "medium_issues": list  (条件付きPASS対象)
        - "low_issues": list  (スキップ可能)
    """
    high_issues = [i for i in issues if i.get("level") == "High"]
    medium_issues = [i for i in issues if i.get("level") == "Medium"]
    low_issues = [i for i in issues if i.get("level") == "Low"]

    if high_issues:
        return {
            "gate_status": "BLOCKED",
            "can_proceed": False,
            "message": (
                f"[HIGH] BLOCKED: {len(high_issues)} 件の致命的 (High) 指摘があります。"
                " 完全修正と再レビュー合格が必須です。次フェーズへの移行をロックします。"
            ),
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "project": project_name,
            "phase": phase,
            "reviewer": reviewer,
        }

    if medium_issues:
        return {
            "gate_status": "CONDITIONAL_PASS",
            "can_proceed": True,
            "message": (
                f"[MEDIUM] 条件付きPASS: {len(medium_issues)} 件の主要 (Medium) 指摘があります。"
                " 修正エビデンスを提出した時点で次工程に進むことを許可します。"
            ),
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "low_issues": low_issues,
            "project": project_name,
            "phase": phase,
            "reviewer": reviewer,
        }

    return {
        "gate_status": "PASS",
        "can_proceed": True,
        "message": (
            f"[PASS] PASS: 致命的・主要指摘なし。"
            f" ({len(low_issues)} 件の軽微指摘はチケット登録で並行修正に回します。)"
        ),
        "high_issues": high_issues,
        "medium_issues": medium_issues,
        "low_issues": low_issues,
        "project": project_name,
        "phase": phase,
        "reviewer": reviewer,
    }
