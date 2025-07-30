from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from src.trustwise.sdk.metrics import base


class DummyRequest:
    def __init__(self, value=None):
        self.value = value

class DummyResponse:
    pass

class DummyModel:
    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar

class DummyClient:
    def __init__(self):
        self._post = MagicMock(return_value="mocked!")

class DummyMetric(base.BaseMetric):
    def evaluate(self, request):
        return f"evaluated: {request.value}"


def test_get_endpoint_url():
    client = DummyClient()
    metric = DummyMetric(client, "https://api.example.com", "v1")
    url = metric._get_endpoint_url("foo")
    assert url == "https://api.example.com/foo"


def test_post_calls_client():
    client = DummyClient()
    metric = DummyMetric(client, "https://api.example.com", "v1")
    metric._post("foo", {"bar": 1})
    client._post.assert_called_once()
    assert client._post.call_args[0][0] == "https://api.example.com/foo"
    assert client._post.call_args[0][1] == {"bar": 1}


def test_batch_evaluate_not_implemented():
    client = DummyClient()
    metric = DummyMetric(client, "https://api.example.com", "v1")
    with pytest.raises(NotImplementedError):
        metric.batch_evaluate([DummyRequest(1)])


def test_explain_not_implemented():
    client = DummyClient()
    metric = DummyMetric(client, "https://api.example.com", "v1")
    with pytest.raises(NotImplementedError):
        metric.explain()


def test_validate_request_model_success():
    req = base.BaseMetric.validate_request_model(DummyModel, foo=1, bar=2)
    assert isinstance(req, DummyModel)
    assert req.foo == 1
    assert req.bar == 2


def test_validate_request_model_validation_error():
    class FailingModel(BaseModel):
        foo: int
    # Missing required field 'foo' should raise a pydantic.ValidationError
    with pytest.raises(base.TrustwiseValidationError):
        base.BaseMetric.validate_request_model(FailingModel)


def test_validate_request_model_type_error_missing_args():
    class Model:
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar
    with pytest.raises(base.TrustwiseValidationError) as excinfo:
        base.BaseMetric.validate_request_model(Model, foo=1)
    msg = str(excinfo.value)
    assert "Invalid arguments" in msg
    assert "bar" in msg


def test_metric_registry_register_and_get():
    reg = base.MetricRegistry()
    reg.register(DummyRequest, lambda x: "ok")
    handler = reg.get_handler(DummyRequest(1))
    assert handler is not None
    assert handler(DummyRequest(1)) == "ok"


def test_metric_registry_get_handler_none():
    reg = base.MetricRegistry()
    assert reg.get_handler(DummyRequest(1)) is None


def test_metric_evaluator_endpoint_name():
    class FooBarMetric(base.MetricEvaluator):
        def evaluate(self, request):
            return "ok"
    metric = FooBarMetric(DummyClient(), "https://api.example.com", "v1")
    assert metric._get_endpoint_name() == "foo_bar"


def test_metric_evaluator_batch_and_explain():
    class DummyEval(base.MetricEvaluator):
        def evaluate(self, request):
            return "ok"
    metric = DummyEval(DummyClient(), "https://api.example.com", "v1")
    with pytest.raises(NotImplementedError):
        metric.batch_evaluate([DummyRequest(1)])
    with pytest.raises(NotImplementedError):
        metric.explain()


def test_base_metric_abstract_instantiation():
    # Should not be able to instantiate BaseMetric directly
    from src.trustwise.sdk.metrics.base import BaseMetric
    with pytest.raises(TypeError):
        BaseMetric(None, None, None)


def test_validate_request_model_type_error_custom_dummy():
    # This triggers the DummyValidationError branch
    class Model:
        def __init__(self, foo, bar):
            if bar is None:
                raise TypeError("bar is required")
            self.foo = foo
            self.bar = bar
    with pytest.raises(base.TrustwiseValidationError) as excinfo:
        base.BaseMetric.validate_request_model(Model, foo=1)
    assert "field required" in str(excinfo.value) or "bar" in str(excinfo.value)


def test_base_safety_metric_evaluate_unregistered():
    metric = base.BaseSafetyMetric(DummyClient(), "https://api.example.com", "v1")
    class Unregistered:
        pass
    with pytest.raises(ValueError):
        metric.evaluate(Unregistered())


def test_base_safety_metric_pii_value_error():
    metric = base.BaseSafetyMetric(DummyClient(), "https://api.example.com", "v1")
    class Dummy:
        text = None
    with pytest.raises(ValueError):
        metric.pii(Dummy())
    class Dummy2:
        text = 123
    with pytest.raises(ValueError):
        metric.pii(Dummy2())


def test_base_safety_metric_prompt_injection_value_error():
    metric = base.BaseSafetyMetric(DummyClient(), "https://api.example.com", "v1")
    class Dummy:
        query = None
    with pytest.raises(ValueError):
        metric.prompt_injection(Dummy())
    class Dummy2:
        query = 123
    with pytest.raises(ValueError):
        metric.prompt_injection(Dummy2())


def test_base_safety_metric_metric_methods_call_post():
    client = DummyClient()
    metric = base.BaseSafetyMetric(client, "https://api.example.com", "v1")
    # Patch registry to avoid ValueError
    metric._registry.register(str, lambda x: "ok")
    # Test all metric methods call _post
    for method, arg in [
        (metric.faithfulness, "foo"),
        (metric.context_relevancy, "foo"),
        (metric.answer_relevancy, "foo"),
        (metric.summarization, "foo"),
        (metric.clarity, "foo"),
        (metric.helpfulness, "foo"),
    ]:
        method(arg)
        assert client._post.called
        client._post.reset_mock()


def test_base_alignment_metric_evaluate_default_to_clarity():
    client = DummyClient()
    metric = base.BaseAlignmentMetric(client, "https://api.example.com", "v1")
    from trustwise.sdk.types import ClarityRequest
    # Should call clarity if request is ClarityRequest
    # Patch registry to always return None
    metric._registry.get_handler = lambda req: None
    # Patch clarity to check call
    called = {}
    def fake_clarity(req):
        called["called"] = True
        return "clarity!"
    metric.clarity = fake_clarity
    result = metric.evaluate(ClarityRequest(query="q", response="r"))
    assert result == "clarity!"
    assert called["called"]
    # Should raise ValueError for other types
    class NotClarity:
        pass
    with pytest.raises(ValueError):
        metric.evaluate(NotClarity())


def test_base_performance_metric_evaluate_and_carbon():
    client = DummyClient()
    metric = base.BasePerformanceMetric(client, "https://api.example.com", "v1")
    # Test evaluate calls cost
    req = {
        "total_prompt_tokens": 1,
        "total_completion_tokens": 2,
        "model_name": "foo",
        "model_provider": "bar",
        "average_latency": 1,
        "number_of_queries": 1,
        "instance_type": "baz"
    }
    metric.evaluate(req)
    assert client._post.called
    client._post.reset_mock()
    # Test carbon
    metric.carbon(
        processor_name="cpu",
        provider_name="aws",
        provider_region="us-east-1",
        instance_type="baz",
        average_latency=1
    )
    assert client._post.called 