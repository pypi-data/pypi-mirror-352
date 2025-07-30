import pytest
from click.testing import CliRunner
from sv_simpleparser.cli import cli


def test_gen_sv_instance_smoke():
    """Simply test that the command runs without errors"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a dummy SV file
        with open("test.sv", "w") as f:
            f.write("module dummy(); endmodule")

        # Run the command
        result = runner.invoke(cli, ["gen-sv-instance", "test.sv"])

        # Just check it didn't crash
        assert result.exit_code == 0


def test_gen_io_table_smoke():
    """Simply test that the command runs without errors"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a dummy SV file
        with open("test.sv", "w") as f:
            f.write("module dummy(); endmodule")

        # Run the command
        result = runner.invoke(cli, ["gen-io-table", "test.sv"])

        # Just check it didn't crash
        assert result.exit_code == 0


def test_cli_help_smoke():
    """Test that help command works"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
