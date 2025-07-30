import pytest
import winzy_pdf_to_text as w

from argparse import ArgumentParser


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result, _ = parser.parse_known_args(["hello", "-p", "1-4"])
    assert result.file_path == "hello"
    assert result.pages == ["1-4"]


def test_plugin(capsys):
    w.pdf2txt_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``winzy`` plugin." in captured.out
