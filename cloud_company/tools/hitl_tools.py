"""
Human-in-the-Loop (HITL) ツール。
重要なビジネス判断ポイントで人間の承認を記録する。

ADK Web における HITL の実装方針:
- `input()` はサーバーのイベントループをブロックするため使用しない。
- 代わりに、ツールは「承認待ち状態」を返し、エージェントがユーザーに
  チャット経由で yes/no の確認を求める。
- ユーザーが次のメッセージで "yes" または "no" を送ると、
  エージェントが判断して次のフェーズへ進む。
"""

import sys


def _safe_print(*args: object) -> None:
    """Windows cp932 環境でも安全に出力するユーティリティ。"""
    text = " ".join(str(a) for a in args)
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()


def request_human_approval(
    checkpoint_name: str,
    context_summary: str,
    required_action: str,
) -> dict[str, str]:
    """
    人間の承認を要求する HITL チェックポイント。

    ADK Web では input() が使えないため、このツールは
    「承認要求メッセージ」を返す。エージェントはこのメッセージを
    ユーザーに表示し、次のユーザー入力（yes/no）を待つ。

    Args:
        checkpoint_name: チェックポイント名 (例: "仮払い完了確認")
        context_summary: 現在の状況サマリ
        required_action: ユーザーに求めるアクション説明

    Returns:
        承認要求の内容を含む辞書。
        - "status": "awaiting_approval"
        - "checkpoint": str
        - "message": str  (ユーザーへの表示メッセージ)
    """
    _safe_print(f"[HITL] Checkpoint reached: {checkpoint_name}")

    message = (
        f"## [HITL] 承認が必要です: {checkpoint_name}\n\n"
        f"### 状況サマリ\n{context_summary}\n\n"
        f"### 必要なアクション\n{required_action}\n\n"
        "---\n"
        "**承認する場合は `yes` と入力してください。**\n"
        "**中断する場合は `no: <理由>` と入力してください。**\n"
        "(例: `no: 予算が合わないため`)"
    )

    return {
        "status": "awaiting_approval",
        "checkpoint": checkpoint_name,
        "message": message,
    }


def confirm_payment_received(
    project_name: str,
    client_name: str,
    amount: str,
) -> dict[str, str]:
    """
    Step 5: 仮払い完了確認の HITL チェックポイント。
    クライアントの仮払い完了を人間が目視確認したことを記録する。

    Args:
        project_name: プロジェクト名
        client_name: クライアント名
        amount: 仮払い金額

    Returns:
        承認要求の内容を含む辞書。
    """
    return request_human_approval(
        checkpoint_name="仮払い完了確認 (Step 5)",
        context_summary=(
            f"- プロジェクト: {project_name}\n"
            f"- クライアント: {client_name}\n"
            f"- 仮払い金額: {amount}\n\n"
            "クラウドワークスの管理画面で仮払い完了を確認してください。"
        ),
        required_action=(
            "クラウドワークスのダッシュボードで仮払い完了を確認し、"
            "`yes` を入力して開発着手を承認してください。"
        ),
    )


def confirm_kickoff(
    project_name: str,
    team_members: list[str],
    kickoff_summary: str,
) -> dict[str, str]:
    """
    Step 8: 社内開発キックオフ承認の HITL チェックポイント。

    Args:
        project_name: プロジェクト名
        team_members: アサインメンバーリスト
        kickoff_summary: キックオフMTGのサマリ

    Returns:
        承認要求の内容を含む辞書。
    """
    members_str = ", ".join(team_members) if team_members else "未確定"
    return request_human_approval(
        checkpoint_name="キックオフ承認 (Step 8)",
        context_summary=(
            f"- プロジェクト: {project_name}\n"
            f"- アサインメンバー: {members_str}\n\n"
            f"キックオフサマリ:\n{kickoff_summary}"
        ),
        required_action=(
            "スコープとメンバーアサインを確認し、"
            "`yes` を入力して開発フェーズへの移行を承認してください。"
        ),
    )


def confirm_delivery(
    project_name: str,
    delivery_summary: str,
    demo_url: str,
) -> dict[str, str]:
    """
    Step 11: 正式納品前の最終確認 HITL チェックポイント。

    Args:
        project_name: プロジェクト名
        delivery_summary: 納品物サマリ
        demo_url: デモ動画URL（またはローカルパス）

    Returns:
        承認要求の内容を含む辞書。
    """
    return request_human_approval(
        checkpoint_name="納品物最終確認 (Step 11)",
        context_summary=(
            f"- プロジェクト: {project_name}\n"
            f"- デモURL: {demo_url}\n\n"
            f"納品物サマリ:\n{delivery_summary}"
        ),
        required_action=(
            "デモ動画とQAテスト結果を確認し、"
            "`yes` を入力してクラウドワークスへの正式納品を承認してください。"
        ),
    )
