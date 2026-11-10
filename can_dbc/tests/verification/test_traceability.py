"""Completeness of the requirement <-> test traceability."""

import pytest

from .conftest import requirement_ids


@pytest.mark.req()
def test_every_requirement_has_a_test_and_every_test_a_requirement(request):
    config = request.config
    if config.option.keyword or config.option.markexpr or len(config.args) != 1:
        pytest.skip("only meaningful when the complete suite is selected")
    known = set(requirement_ids())
    assert len(known) >= 20, "requirements document not parsed"
    referenced = set()
    for item in request.session.items:
        ids = [i for mark in item.iter_markers("req") for i in mark.args]
        if item.name.startswith(("test_every_requirement", "test_golden_vectors_cover")):
            continue
        assert ids, f"test without requirement: {item.nodeid}"
        assert set(ids) <= known, f"unknown requirement in {item.nodeid}: {set(ids) - known}"
        referenced |= set(ids)
    assert known - referenced == set(), f"requirements without test: {sorted(known - referenced)}"
