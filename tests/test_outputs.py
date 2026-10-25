"""Verifier: exact string equality on every answer, all-or-nothing."""
import json
import os
import re

import pytest

ANSWERS = os.environ.get("ANSWERS_PATH", "/app/answers.json")
EXPECTED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expected.json")
DECIMAL = re.compile(r"^(0|[1-9][0-9]*)$")


@pytest.fixture(scope="module")
def expected():
    with open(EXPECTED) as f:
        return json.load(f)["answers"]


@pytest.fixture(scope="module")
def answers():
    assert os.path.exists(ANSWERS), f"{ANSWERS} was not written"
    with open(ANSWERS) as f:
        data = json.load(f)
    assert isinstance(data, dict) and isinstance(data.get("answers"), dict), \
        'answers.json must be {"answers": {id: "value", ...}}'
    return data["answers"]


def test_every_id_present(answers, expected):
    missing = sorted(set(expected) - set(answers))
    assert not missing, f"missing ids: {missing}"


def test_values_are_decimal_strings(answers, expected):
    bad = [i for i in expected if not (isinstance(answers.get(i), str) and DECIMAL.match(answers[i]))]
    assert not bad, f"not canonical decimal strings: {bad}"


def test_all_values_exact(answers, expected):
    wrong = [i for i in sorted(expected) if answers.get(i) != expected[i]]
    assert not wrong, f"{len(wrong)} wrong answer(s): {wrong}"
