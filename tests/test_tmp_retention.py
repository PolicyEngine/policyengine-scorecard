"""pytest.ini's tmp_path retention, as pytest applies it.

Inner pytest sessions run under the repository's own pytest.ini and check
what its comment says. A passing test's tmp_path goes when the test ends.
A test whose body fails or skips keeps its folder. A test whose error is in
setup or teardown keeps nothing. And a session that passes leaves no
basetemp behind. Under pytest's default policy ("all"), every one of those
folders would stay.
"""

import sys
from pathlib import Path

pytest_plugins = ["pytester"]

INI = Path(__file__).resolve().parent.parent / "pytest.ini"

OUTCOMES = """
import pytest


@pytest.fixture
def broken_setup(tmp_path):
    (tmp_path / "evidence").write_text("x")
    raise RuntimeError("setup")


@pytest.fixture
def broken_teardown():
    yield
    raise RuntimeError("teardown")


def test_passes(tmp_path):
    (tmp_path / "evidence").write_text("x")


def test_fails(tmp_path):
    (tmp_path / "evidence").write_text("x")
    assert False


def test_skips_in_its_body(tmp_path):
    (tmp_path / "evidence").write_text("x")
    pytest.skip("inside the body")


def test_errors_in_setup(broken_setup):
    pass


def test_errors_in_teardown(tmp_path, broken_teardown):
    (tmp_path / "evidence").write_text("x")
"""


def test_only_a_body_that_does_not_pass_keeps_its_tmp_path(pytester):
    pytester.makefile(".ini", pytest=INI.read_text())
    pytester.makepyfile(test_outcomes=OUTCOMES)
    basetemp = pytester.path.parent / "inner-basetemp"
    result = pytester.runpytest("-p", "no:cacheprovider", f"--basetemp={basetemp}")
    # test_errors_in_teardown counts once as passed and once as an error.
    result.assert_outcomes(passed=2, failed=1, skipped=1, errors=2)
    # Folders only: pytest also points a "test_failscurrent" link at the one
    # it keeps.
    left = sorted(p.name for p in basetemp.iterdir() if not p.is_symlink())
    assert left == ["test_fails0", "test_skips_in_its_body0"], left
    for kept in left:
        assert (basetemp / kept / "evidence").read_text() == "x"


def test_a_passing_session_leaves_no_basetemp(pytester, monkeypatch):
    """With no --basetemp, as a plain `pytest tests/` runs: pytest makes the
    session's basetemp under PYTEST_DEBUG_TEMPROOT (else the system temp
    folder) and deletes it when the session passes."""
    root = pytester.path.parent / "temproot"
    root.mkdir()
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(root))
    pytester.makefile(".ini", pytest=INI.read_text())
    pytester.makepyfile(
        test_passing="def test_writes(tmp_path):\n"
        "    (tmp_path / 'evidence').write_text('x')\n"
    )
    result = pytester.run(sys.executable, "-m", "pytest", "-p", "no:cacheprovider")
    assert result.ret == 0, result.stdout.str()
    sessions = [p for p in root.glob("pytest-of-*/pytest-*") if p.is_dir()]
    assert sessions == [], sessions
    assert list(root.rglob("evidence")) == []
