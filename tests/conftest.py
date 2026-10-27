import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


@pytest.fixture
def private_candidate():
    return load("examples/valid/candidate-supply-chain-analyst.full-private.json")


@pytest.fixture
def shared_candidate():
    return load("examples/valid/candidate-supply-chain-analyst.shared-view.json")


@pytest.fixture
def job():
    return load("examples/valid/job-demand-planner.public.json")


@pytest.fixture
def agency_job():
    return load("examples/valid/job-supply-planner-agency.public.json")


@pytest.fixture
def policies():
    return load("examples/policies/demo-hiring-fit.policy.json"), load("examples/policies/demo-career-fit.policy.json")
