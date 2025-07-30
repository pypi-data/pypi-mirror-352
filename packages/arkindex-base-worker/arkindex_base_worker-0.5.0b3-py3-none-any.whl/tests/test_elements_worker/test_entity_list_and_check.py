import pytest
from responses import matchers

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Transcription
from arkindex_worker.worker.entity import MissingEntityType
from tests import CORPUS_ID

from . import BASE_API_CALLS


def test_create_entity_type_wrong_name(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity_type(name=None)

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity_type(name=1234)


def test_create_entity_type_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/entity/types/")]


def test_create_entity_type_already_exists(responses, mock_elements_worker):
    assert mock_elements_worker.entity_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=400,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/entity-types/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {"id": "lastname-id", "name": "lastname", "color": "ffd1b3"},
                {"id": "firstname-id", "name": "firstname", "color": "ffd1b3"},
            ],
        },
    )

    mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/types/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/entity-types/"),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {
        "lastname": "lastname-id",
        "firstname": "firstname-id",
    }


def test_create_entity_type(responses, mock_elements_worker):
    assert mock_elements_worker.entity_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=200,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
        json={
            "id": "firstname-id",
            "name": "firstname",
            "corpus": CORPUS_ID,
            "color": "ffd1b3",
        },
    )

    mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/types/"),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {"firstname": "firstname-id"}


def test_check_required_entity_types_wrong_entity_types(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="entity_types shouldn't be null and should be of type list",
    ):
        mock_elements_worker.check_required_entity_types(entity_types=None)

    with pytest.raises(
        AssertionError,
        match="entity_types shouldn't be null and should be of type list",
    ):
        mock_elements_worker.check_required_entity_types(entity_types=1234)

    with pytest.raises(
        AssertionError,
        match="Entity type at index 1 in entity_types: Should be of type str",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname", 1234]
        )


def test_check_required_entity_types_wrong_create_missing(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname"], create_missing=None
        )

    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname"], create_missing=1234
        )


def test_check_required_entity_types_do_not_create_missing(
    responses, mock_elements_worker
):
    # Set one entity type
    mock_elements_worker.entity_types = {"lastname": "lastname-id"}

    with pytest.raises(
        MissingEntityType, match="Entity type `firstname` was not in the corpus."
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["lastname", "firstname"], create_missing=False
        )

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_check_required_entity_types(responses, mock_elements_worker):
    # Set one entity type
    mock_elements_worker.entity_types = {"lastname": "lastname-id"}

    # Call to create a new entity type
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=200,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
        json={
            "id": "firstname-id",
            "name": "firstname",
            "corpus": CORPUS_ID,
            "color": "ffd1b3",
        },
    )

    mock_elements_worker.check_required_entity_types(
        entity_types=["lastname", "firstname"], create_missing=True
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/entity/types/",
        ),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {
        "lastname": "lastname-id",
        "firstname": "firstname-id",
    }


def test_list_transcription_entities_deprecation(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_version = "worker_version_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_version=worker_version,
        response={"id": "entity_id"},
    )
    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        assert fake_dummy_worker.list_transcription_entities(
            transcription, worker_version=worker_version
        ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_transcription_entities(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_run = "worker_run_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_run=worker_run,
        response={"id": "entity_id"},
    )
    assert fake_dummy_worker.list_transcription_entities(
        transcription, worker_run=worker_run
    ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_corpus_entities(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/entities/",
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "fake_entity_id",
                }
            ],
        },
    )

    mock_elements_worker.list_corpus_entities()

    assert mock_elements_worker.entities == {
        "fake_entity_id": {
            "id": "fake_entity_id",
        }
    }

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/entities/",
        ),
    ]


@pytest.mark.parametrize("wrong_name", [1234, 12.5])
def test_list_corpus_entities_wrong_name(mock_elements_worker, wrong_name):
    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_corpus_entities(name=wrong_name)


@pytest.mark.parametrize("wrong_parent", [{"id": "element_id"}, 12.5, "blabla"])
def test_list_corpus_entities_wrong_parent(mock_elements_worker, wrong_parent):
    with pytest.raises(AssertionError, match="parent should be of type Element"):
        mock_elements_worker.list_corpus_entities(parent=wrong_parent)
