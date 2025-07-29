from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from flask.testing import FlaskClient

from . import _initialize_ucam_faas_app

if TYPE_CHECKING:
    from typing_extensions import Never


class CreateEventAppClientFn(Protocol):
    def __call__(self, target: str, source: str | Path | None = None) -> FlaskClient:
        ...


try:
    if TYPE_CHECKING:
        from cloudevents.pydantic.v2 import CloudEvent
    else:
        from cloudevents.pydantic import CloudEvent
    from polyfactory.factories.pydantic_factory import ModelFactory
    from pytest import fixture

    @fixture
    def event_app_test_client_factory() -> CreateEventAppClientFn:
        def _event_app_client(target: str, source: str | Path | None = None) -> FlaskClient:
            test_app = _initialize_ucam_faas_app(target, source)
            return test_app.test_client()

        return _event_app_client

    class CloudEventFactory(ModelFactory[CloudEvent]):
        __model__ = CloudEvent

        specversion = "1.0"

except ImportError as e:
    _import_error = e

    @fixture
    def event_app_test_client_factory() -> Never:
        raise RuntimeError(
            f"Fixture {event_app_test_client_factory.__name__} is not available "
            f"because ucam_faas is not installed with the 'testing' extra]"
        ) from _import_error
