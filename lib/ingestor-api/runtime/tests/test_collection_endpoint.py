from unittest.mock import patch

publish_collections_endpoint = "/collections"
delete_collection_endpoint = "/collections/{collection_id}"


@patch("src.collection.ingest")
def test_auth_publish_collection(
    ingest, stac_collection, example_stac_collection, client_authenticated
):
    token = "token"
    response = client_authenticated.post(
        publish_collections_endpoint,
        headers={"Authorization": f"bearer {token}"},
        json=example_stac_collection,
    )
    ingest.assert_called_once_with(stac_collection)
    assert response.status_code == 201


def test_unauth_publish_collection(client, example_stac_collection):
    response = client.post(publish_collections_endpoint, json=example_stac_collection)
    assert response.status_code == 403


@patch("src.collection.delete")
def test_auth_delete_collection(delete, example_stac_collection, client_authenticated):
    token = "token"
    response = client_authenticated.delete(
        delete_collection_endpoint.format(collection_id=example_stac_collection["id"]),
        headers={"Authorization": f"bearer {token}"},
    )
    delete.assert_called_once_with(collection_id=example_stac_collection["id"])
    assert response.status_code == 200


def test_unauth_delete_collection(client, example_stac_collection):
    response = client.delete(
        delete_collection_endpoint.format(collection_id=example_stac_collection["id"]),
    )
    assert response.status_code == 403
