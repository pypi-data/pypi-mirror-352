import json
from urllib.parse import unquote

from flask import Request, Response
from google.cloud import pubsub_v1  # type: ignore[import-untyped]
from ucam_observe import get_structlog_logger  # type: ignore[import-untyped]

from ucam_faas.entra.config import settings

logger = get_structlog_logger()


def entra_webhook(request: Request) -> Response:
    if request.method != "POST":
        logger.error("Invalid method received", method=request.method)
        return Response("Method not allowed", status=405)

    validation_token = request.args.get("validationToken")
    if validation_token:
        logger.info("Received validation request from Entra", validation_token=validation_token)
        return Response(unquote(validation_token), status=200, content_type="text/plain")

    try:
        data = request.get_json()
        if not data:
            raise ValueError("Empty JSON payload")
    except Exception as e:
        logger.exception("Invalid JSON payload", error=str(e))
        return Response("Bad Request", status=400)

    service_principal_guid = request.headers.get("X-Service-Principal-Guid")
    if service_principal_guid != settings.expected_service_principal_guid:
        logger.warning(
            "Invalid Service Principal",
            expected=settings.expected_service_principal_guid,
            received=service_principal_guid,
        )
        return Response("Unauthorized", status=401)

    try:
        publisher = pubsub_v1.PublisherClient()
        future = publisher.publish(
            settings.pubsub_topic_path,
            json.dumps(data).encode("utf-8"),
        )
        future.result()
        logger.info("Entra event published", data=data)
    except Exception as e:
        logger.exception("Publishing failed", error=str(e))
        return Response("Internal Server Error", status=500)

    return Response("OK", status=200)
