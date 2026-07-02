"""
ツール単体テスト。
"""

import pytest
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# テスト前に OUTPUT_DIR をテンポラリに設定
import os
os.environ.setdefault("OUTPUT_DIR", "./output_test")
os.environ.setdefault("CLOUD_COMPANY_PATH", "../cloud-company")


class TestProjectTools:
    """project_tools.py の単体テスト。"""

    def test_kebab_conversion(self) -> None:
        """日本語・スペースがケバブケースに変換されることを確認。"""
        from cloud_company.tools.project_tools import _kebab_safe

        assert _kebab_safe("美容室予約システム") == ""  # 日本語は空になる（ハイフンのみ除去）
        assert _kebab_safe("my salon saas") == "my-salon-saas"
        assert _kebab_safe("MyProject2024") == "myproject2024"
        assert _kebab_safe("  test--project  ") == "test-project"

    def test_create_project_folder(self, tmp_path: Path) -> None:
        """プロジェクトフォルダ作成の基本動作を確認。"""
        import cloud_company

        # OUTPUT_DIR をテンポラリに差し替え
        original = cloud_company.OUTPUT_DIR
        cloud_company.OUTPUT_DIR = tmp_path

        try:
            from cloud_company.tools.project_tools import create_project_folder

            result = create_project_folder("test-project-2024")
            assert result["status"] == "created"
            assert result["project_name"] == "test-project-2024"
            assert (tmp_path / "test-project-2024" / "phase-4-design-development").exists()
            assert (tmp_path / "test-project-2024" / "incidents").exists()
        finally:
            cloud_company.OUTPUT_DIR = original

    def test_save_and_read_document(self, tmp_path: Path) -> None:
        """ドキュメントの保存と読み込みが正常に動作することを確認。"""
        import cloud_company

        original = cloud_company.OUTPUT_DIR
        cloud_company.OUTPUT_DIR = tmp_path

        try:
            from cloud_company.tools.project_tools import save_document, read_document

            content = "# テスト\nこれはテストドキュメントです。"
            save_result = save_document(
                "test-project",
                "phase-4-design-development",
                "test-doc.md",
                content,
            )
            assert save_result["status"] == "saved"

            read_result = read_document(
                "test-project",
                "phase-4-design-development",
                "test-doc.md",
            )
            assert read_result["status"] == "ok"
            assert read_result["content"] == content
        finally:
            cloud_company.OUTPUT_DIR = original

    def test_read_nonexistent_document(self, tmp_path: Path) -> None:
        """存在しないファイルの読み込みでエラーを返すことを確認。"""
        import cloud_company

        original = cloud_company.OUTPUT_DIR
        cloud_company.OUTPUT_DIR = tmp_path

        try:
            from cloud_company.tools.project_tools import read_document

            result = read_document("nonexistent", "phase-4-design-development", "missing.md")
            assert "error" in result
        finally:
            cloud_company.OUTPUT_DIR = original


class TestReviewTools:
    """review_tools.py の単体テスト。"""

    def test_review_gate_blocked_on_high(self) -> None:
        """High 指摘がある場合に BLOCKED が返ることを確認。"""
        from cloud_company.tools.review_tools import review_gate

        issues = [
            {"level": "High", "description": "致命的なSQLインジェクション脆弱性"},
            {"level": "Low", "description": "ボタンの色が微妙"},
        ]
        result = review_gate("test-project", "phase-4", "QAリーダー", issues)
        assert result["gate_status"] == "BLOCKED"
        assert result["can_proceed"] is False
        assert len(result["high_issues"]) == 1

    def test_review_gate_conditional_pass_on_medium(self) -> None:
        """High なしで Medium ある場合に CONDITIONAL_PASS が返ることを確認。"""
        from cloud_company.tools.review_tools import review_gate

        issues = [
            {"level": "Medium", "description": "エラーハンドリングが不足"},
            {"level": "Low", "description": "ログ出力が冗長"},
        ]
        result = review_gate("test-project", "phase-4", "QAリーダー", issues)
        assert result["gate_status"] == "CONDITIONAL_PASS"
        assert result["can_proceed"] is True

    def test_review_gate_pass_on_low_only(self) -> None:
        """Low のみの場合に PASS が返ることを確認。"""
        from cloud_company.tools.review_tools import review_gate

        issues = [{"level": "Low", "description": "コメントが少ない"}]
        result = review_gate("test-project", "phase-4", "QAリーダー", issues)
        assert result["gate_status"] == "PASS"
        assert result["can_proceed"] is True

    def test_review_gate_pass_on_no_issues(self) -> None:
        """指摘なしの場合に PASS が返ることを確認。"""
        from cloud_company.tools.review_tools import review_gate

        result = review_gate("test-project", "phase-5", "PMOリーダー", [])
        assert result["gate_status"] == "PASS"
        assert result["can_proceed"] is True


class TestAgentSetup:
    """エージェント構成の基本確認テスト。"""

    def test_root_agent_exists(self) -> None:
        """root_agent が正常にインポートできることを確認。"""
        from cloud_company.agent import root_agent

        assert root_agent is not None
        assert root_agent.name == "cloud_company_orchestrator"

    def test_root_agent_has_seven_phases(self) -> None:
        """root_agent に7フェーズのサブエージェントが存在することを確認。"""
        from cloud_company.agent import root_agent

        assert len(root_agent.sub_agents) == 7

    def test_phase4_has_parallel_agent(self) -> None:
        """Phase 4 に ParallelAgent が含まれることを確認。"""
        from google.adk.agents import ParallelAgent
        from cloud_company.agents.phase4_development import development_phase

        has_parallel = any(
            isinstance(agent, ParallelAgent)
            for agent in development_phase.sub_agents
        )
        assert has_parallel, "Phase 4 に ParallelAgent が見つかりません"
