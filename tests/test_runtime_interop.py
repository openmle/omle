"""Tests for OMLEModel's runtime interop — to_runtime and the sklearn-style API.

The cached handle is deliberately invisible to the document: it must not reach
to_dict, JSON, pickles or copies. Those checks need no runtime installed, so
they always run. Scoring itself is skipped unless omle-runtime is present.
"""

import copy
import json
import pickle

import pytest

import omle

try:
    import omle_runtime
except ImportError:  # the runtime is an optional extra
    omle_runtime = None

requires_runtime = pytest.mark.skipif(
    omle_runtime is None, reason="omle-runtime not installed")


@pytest.fixture()
def model():
    """A minimal scoreable model: one input, one identity-ish node."""
    return omle.OMLEModel(metadata=omle.ModelMetadata(name="interop"))


# ── the cache must stay out of the document ───────────────────────────────────

class TestCacheIsInvisible:
    def test_to_dict_omits_the_cache(self, model):
        model._runtime = object()
        assert not any(k.startswith("_") for k in model.to_dict())

    def test_json_still_serializes(self, model):
        model._runtime = object()
        json.dumps(model.to_dict())          # must not raise

    def test_pickle_drops_the_cache(self, model):
        model._runtime = object()
        assert getattr(pickle.loads(pickle.dumps(model)), "_runtime", None) is None

    def test_deepcopy_drops_the_cache(self, model):
        model._runtime = object()
        assert getattr(copy.deepcopy(model), "_runtime", None) is None

    def test_equality_ignores_the_cache(self, model):
        other = omle.OMLEModel(metadata=omle.ModelMetadata(name="interop"))
        model._runtime = object()
        assert model == other


# ── invalidation ──────────────────────────────────────────────────────────────

class TestInvalidate:
    def test_invalidate_clears_the_handle(self, model):
        model._runtime = object()
        model.invalidate_runtime()
        assert model._runtime is None

    def test_invalidate_is_safe_before_any_build(self, model):
        model.invalidate_runtime()           # must not raise
        assert model._runtime is None


# ── to_runtime ────────────────────────────────────────────────────────────────

@requires_runtime
class TestToRuntime:
    """to_runtime is a factory: always fresh, never the cached handle."""

    def test_returns_a_runtime_model(self, model):
        assert isinstance(model.to_runtime(), omle_runtime.Model)

    def test_every_call_builds_a_new_handle(self, model):
        assert model.to_runtime() is not model.to_runtime()

    def test_does_not_populate_the_predict_cache(self, model):
        model.to_runtime()
        assert getattr(model, "_runtime", None) is None

    def test_never_returns_the_cached_handle(self, model):
        cached = model._runtime_for_predict()
        assert model.to_runtime() is not cached

    def test_accepts_runtime_options(self, model):
        assert isinstance(model.to_runtime(n_threads=2), omle_runtime.Model)

    def test_an_unpickled_model_can_still_build_one(self, model):
        model.to_runtime()
        revived = pickle.loads(pickle.dumps(model))
        assert isinstance(revived.to_runtime(), omle_runtime.Model)


@requires_runtime
class TestPredictCache:
    """predict and predict_proba share one lazily built handle."""

    def test_cache_starts_empty(self, model):
        assert getattr(model, "_runtime", None) is None

    def test_first_use_populates_the_cache(self, model):
        runtime = model._runtime_for_predict()
        assert model._runtime is runtime

    def test_second_use_reuses_it(self, model):
        assert model._runtime_for_predict() is model._runtime_for_predict()

    def test_invalidate_forces_a_rebuild(self, model):
        first = model._runtime_for_predict()
        model.invalidate_runtime()
        assert model._runtime_for_predict() is not first
