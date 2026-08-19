import json
import subprocess

import pytest
from stactools_item_generator.item import ItemRequest, create_stac_item


@pytest.fixture
def mock_stactools_command(monkeypatch):
    commands = []

    def _run(command, capture_output, text, check):
        commands.append(command)
        with open(command[-1], "w") as output:
            json.dump(
                {
                    "type": "Feature",
                    "stac_version": "1.0.0",
                    "id": "test-item",
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "links": [],
                    "assets": {},
                    "bbox": [0, 0, 0, 0],
                    "stac_extensions": [],
                },
                output,
            )
        return subprocess.CompletedProcess(
            args=command, returncode=0, stdout="ok", stderr=""
        )

    monkeypatch.setattr("stactools_item_generator.item.subprocess.run", _run)
    return commands


@pytest.mark.parametrize(
    "item_request",
    [
        ItemRequest(
            package_name="stactools-glad-glclu2020",
            group_name="gladglclu2020",
            create_item_args=[
                "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/2000/50N_090W.tif"
            ],
            collection_id=None,
        ),
        ItemRequest(
            package_name="stactools-glad-global-forest-change==0.1.2",
            group_name="gladglobalforestchange",
            create_item_args=[
                "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_40N_080W.tif",
                "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_treecover2000_40N_080W.tif",
                "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_lossyear_40N_080W.tif",
                "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_datamask_40N_080W.tif",
            ],
            collection_id=None,
        ),
        ItemRequest(
            package_name="stactools-glad-glclu2020",
            group_name="gladglclu2020",
            create_item_args=[
                "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/2000/50N_090W.tif"
            ],
            collection_id="test",
        ),
    ],
)
def test_item(item_request: ItemRequest, mock_stactools_command: list[list[str]]) -> None:
    stac_item = create_stac_item(item_request)
    command = mock_stactools_command[0]
    assert command[0] == "uvx"
    assert command[2].endswith(item_request.package_name)
    if item_request.collection_id:
        assert stac_item.collection == item_request.collection_id
