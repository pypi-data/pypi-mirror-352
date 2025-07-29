import json
from typing import Tuple
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask import Response as FlaskResponse
from flask import request as flask_request
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from ucam_faas.entra.config import settings
from ucam_faas.entra.handler import entra_webhook


@pytest.fixture
def app_with_mock_publisher(mocker: MockerFixture) -> Tuple[Flask, MagicMock]:
    mock_publisher_constructor = mocker.patch("ucam_faas.entra.handler.pubsub_v1.PublisherClient")

    mock_publisher_instance = MagicMock()
    mock_publish_method = MagicMock()
    mock_future = MagicMock()
    mock_future.result.return_value = None
    mock_publish_method.return_value = mock_future
    mock_publisher_instance.publish = mock_publish_method
    mock_publisher_constructor.return_value = mock_publisher_instance

    app = Flask(__name__)

    def view_func_wrapper() -> FlaskResponse:
        return entra_webhook(flask_request)

    app.route("/", methods=["POST", "GET"])(view_func_wrapper)
    return app, mock_publish_method


@pytest.fixture
def client(app_with_mock_publisher: Tuple[Flask, MagicMock]) -> FlaskClient:
    app, _ = app_with_mock_publisher
    return app.test_client()


@pytest.fixture
def mock_publish(app_with_mock_publisher: Tuple[Flask, MagicMock]) -> MagicMock:
    _, mock_publish_method = app_with_mock_publisher
    return mock_publish_method


def test_validation_token(client: FlaskClient) -> None:
    response = client.post("/?validationToken=abc123")
    assert response.status_code == 200
    assert response.data.decode() == "abc123"


def test_invalid_method(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 405


def test_invalid_principal(client: FlaskClient) -> None:
    response = client.post(
        "/",
        json={"key": "value"},
        headers={"X-Service-Principal-Guid": "invalid-guid"},
    )
    assert response.status_code == 401


def test_publish_event(client: FlaskClient, mock_publish: MagicMock) -> None:
    test_payload = {"key": "value"}
    response = client.post(
        "/",
        json=test_payload,
        headers={"X-Service-Principal-Guid": settings.expected_service_principal_guid},
    )

    assert response.status_code == 200

    expected_data_bytes = json.dumps(test_payload).encode("utf-8")
    mock_publish.assert_called_once_with(settings.pubsub_topic_path, expected_data_bytes)
