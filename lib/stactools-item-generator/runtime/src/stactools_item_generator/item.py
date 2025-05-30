import json
import logging
import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from stac_pydantic.item import Item

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ItemRequest(BaseModel):
    package_name: str = Field(..., description="Name of the stactools package")
    group_name: str = Field(..., description="Group name for the STAC item")
    create_item_args: List[str] = Field(
        ..., description="Arguments for create-item command"
    )
    create_item_options: Dict[str, str] = Field(
        default_factory=dict, description="Options for create-item command"
    )
    collection_id: Optional[str] = Field(
        None, description="value for the collection field of the item json"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "package_name": "stactools-glad-glclu2020",
                "group_name": "gladglclu2020",
                "create_item_args": [
                    "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/2000/50N_090W.tif"
                ],
            }
        }
    )


def create_stac_item(request: ItemRequest) -> Item:
    """
    Create a STAC item using a stactools package
    """
    logger.info(f"Received request: {json.dumps(request.model_dump())}")

    if not request.package_name:
        raise ValueError("Missing required parameter: package_name")

    command = [
        "uvx",
        "--with",
        f"requests,{request.package_name}",
        "--from",
        "stactools",
        "stac",
        request.group_name,
        "create-item",
        *request.create_item_args,
    ]

    for option, value in request.create_item_options.items():
        command.extend([f"--{option}", value])

    logger.info(f"Executing command: {' '.join(command)}")

    with NamedTemporaryFile(suffix=".json") as output:
        command.append(output.name)
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        logger.info(f"Command output: {result.stdout}")
        with open(output.name) as f:
            item_dict = json.load(f)

    if request.collection_id:
        item_dict["collection"] = request.collection_id

    return Item(**item_dict)
