import pytest
from stac_item_generator.item import ItemRequest, create_stac_item


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
def test_item(item_request: ItemRequest) -> None:
    stac_item = create_stac_item(item_request)
    if item_request.collection_id:
        assert stac_item.collection == item_request.collection_id
