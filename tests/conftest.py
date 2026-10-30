"""Root pytest configuration."""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--proto-json",
        action="store_true",
        default=True,
        help="Print JSON representation of generated proto models in proto-convert tests (default: True)",
    )


@pytest.fixture
def proto_json(request):
    return request.config.getoption("--proto-json")
