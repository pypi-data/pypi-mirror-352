"""
Unit tests for greetings.py
"""
import sys
from hungovercoders_template_python_package import greetings


def test_hello_output(capsys):
    """Test that hello prints the correct greeting."""
    greetings.hello("Alice")
    captured = capsys.readouterr()
    assert "Hungovercoders say hello to Alice!" in captured.out


def test_hello_cli_default(monkeypatch, capsys):
    """Test hello_cli with default argument (no --name)."""
    test_args = ["prog"]
    monkeypatch.setattr(sys, "argv", test_args)
    greetings.hello_cli()
    captured = capsys.readouterr()
    assert "Hungovercoders say hello to World!" in captured.out


def test_hello_cli_with_name(monkeypatch, capsys):
    """Test hello_cli with --name argument."""
    test_args = ["prog", "--name", "Bob"]
    monkeypatch.setattr(sys, "argv", test_args)
    greetings.hello_cli()
    captured = capsys.readouterr()
    assert "Hungovercoders say hello to Bob!" in captured.out
    def test_goodbye_output(capsys):
        """Test that goodbye prints the correct farewell."""
        greetings.goodbye("Charlie")
        captured = capsys.readouterr()
        assert "Hungovercoders say goodbye to Charlie!" in captured.out

def test_goodbye_cli_default(monkeypatch, capsys):
    """Test goodbye_cli with default argument (no --name)."""
    test_args = ["prog"]
    monkeypatch.setattr(sys, "argv", test_args)
    greetings.goodbye_cli()
    captured = capsys.readouterr()
    assert "Hungovercoders say goodbye to World!" in captured.out

def test_goodbye_cli_with_name(monkeypatch, capsys):
    """Test goodbye_cli with --name argument."""
    test_args = ["prog", "--name", "Dana"]
    monkeypatch.setattr(sys, "argv", test_args)
    greetings.goodbye_cli()
    captured = capsys.readouterr()
    assert "Hungovercoders say goodbye to Dana!" in captured.out