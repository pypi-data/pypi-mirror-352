from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
import structlog
from cloudevents import conversion
from flask import Flask

from ucam_faas import FaaSGunicornApplication, cloud_event, raw_event, run_ucam_faas
from ucam_faas.exceptions import UCAMFAASCouldNotProcess
from ucam_faas.testing import CloudEventFactory, CreateEventAppClientFn

if TYPE_CHECKING:
    from typing_extensions import Never

THIS_FILE_PATH = "ucam_faas/tests/test_ucam_faas.py"


# Raw events
@raw_event
def example_raw_event_no_exception(event: bytes) -> None:
    pass


@raw_event
def example_raw_event_handled_exception(event: bytes) -> Never:
    raise UCAMFAASCouldNotProcess


@raw_event
def example_raw_event_unhandled_exception(event: bytes) -> Never:
    raise Exception("Did not expect this")


# Cloud Events
@cloud_event
def example_cloud_event_no_exception(event: Any) -> None:
    pass


@cloud_event
def example_cloud_event_handled_exception(event: Any) -> None:
    raise UCAMFAASCouldNotProcess


@cloud_event
def example_cloud_event_unhandled_exception(event: Any) -> None:
    raise Exception("Did not expect this")


def test_faas_gunicorn_application_bind() -> None:
    app = Flask(__name__)
    application = FaaSGunicornApplication(app, "0.0.0.0", "8080")

    with patch("gunicorn.app.base.BaseApplication.run") as mock_run:
        application.run()
        mock_run.assert_called_once()  # Ensures that the server's run method was indeed called


@pytest.mark.parametrize(
    "target_tuple",
    [
        (
            "example_raw_event_no_exception",
            "example_raw_event_handled_exception",
            "example_raw_event_unhandled_exception",
        ),
        (
            "example_cloud_event_no_exception",
            "example_cloud_event_handled_exception",
            "example_cloud_event_unhandled_exception",
        ),
    ],
)
def test_exceptions_raw_events(
    event_app_test_client_factory: CreateEventAppClientFn, target_tuple: tuple[str, str, str]
) -> None:
    # Both raw and cloud event functions except cloud eventd
    valid_cloud_event = conversion.to_dict(CloudEventFactory.build())

    # No exception
    test_client = event_app_test_client_factory(target=target_tuple[0], source=THIS_FILE_PATH)
    response = test_client.post("/", json=valid_cloud_event)
    assert response.status_code == 200

    # Handle exception
    test_client = event_app_test_client_factory(target=target_tuple[1], source=THIS_FILE_PATH)
    response = test_client.post("/", json=valid_cloud_event)
    assert response.status_code == 500
    assert "The function raised UCAMFAASCouldNotProcess" in response.data.decode()

    # Unhandled exception
    test_client = event_app_test_client_factory(target=target_tuple[2], source=THIS_FILE_PATH)
    with structlog.testing.capture_logs() as cap_logs:
        response = test_client.post("/", json=valid_cloud_event)
    assert response.status_code == 500

    assert len(cap_logs) == 1
    log_call = cap_logs[0]
    assert (
        log_call.get("event") == "function_failed_uncaught_exception"
        # structlog will include exception details in rendered log message
        and log_call.get("exc_info") is True
    )


@pytest.mark.parametrize(
    "target,expected_return",
    [
        ("example_raw_event_no_exception", 0),
        ("example_raw_event_handled_exception", 1),
        ("example_raw_event_unhandled_exception", 2),
        ("example_cloud_event_no_exception", 0),
        ("example_cloud_event_handled_exception", 1),
        ("example_cloud_event_unhandled_exception", 2),
    ],
)
def test_long_running(target: str, expected_return: int) -> None:
    assert (
        run_ucam_faas(
            target,
            source=THIS_FILE_PATH,
            host="no-host",
            port=0,
            debug=False,
            long_running=True,
        )
        == expected_return
    )
