from cloudevents.pydantic.v2 import CloudEvent

from ucam_faas.testing import CloudEventFactory


def test_cloudeventfactory_model_static_type_has_pydantic_methods() -> None:
    event = CloudEventFactory.build()
    assert CloudEvent.model_validate(event.model_dump()) == event

    # However type checkers don't see Pydantic methods on cloudevents.pydantic.CloudEvent
    from cloudevents.pydantic import CloudEvent as CloudEventAutoVersion

    # mypy complains: "type[CloudEvent]" has no attribute "model_validate"
    assert CloudEventAutoVersion.model_validate(event.model_dump()) == event  # type: ignore[attr-defined] # noqa: E501
