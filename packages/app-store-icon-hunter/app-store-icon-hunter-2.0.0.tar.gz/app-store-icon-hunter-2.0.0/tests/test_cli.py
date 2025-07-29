"""
Tests for CLI functionality
"""

import pytest
from click.testing import CliRunner
from app_store_icon_hunter.cli.main import cli


class TestCLI:
    """Test CLI commands"""
    
    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "App Store Icon Hunter" in result.output
    
    def test_search_command_help(self):
        """Test search command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['search', '--help'])
        assert result.exit_code == 0
        assert "Search for apps" in result.output
    
    def test_list_command_help(self):
        """Test list command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['list', '--help'])
        assert result.exit_code == 0
        assert "Search and list apps" in result.output


if __name__ == "__main__":
    pytest.main([__file__])
