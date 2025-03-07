import base64
import binascii
import enum
import json
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from urllib.parse import urlparse

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    Json,
    PositiveInt,
    dataclasses,
    error_wrappers,
    field_validator,
)
from stac_pydantic import Collection, Item, shared

from . import validators

if TYPE_CHECKING:
    from . import services


class AccessibleAsset(shared.Asset):
    @field_validator("href")
    def is_accessible(cls, href):
        url = urlparse(href)

        if url.scheme in ["https", "http"]:
            validators.url_is_accessible(href=href)
        elif url.scheme in ["s3"]:
            validators.s3_object_is_accessible(
                bucket=url.hostname, key=url.path.lstrip("/")
            )
        else:
            ValueError(f"Unsupported scheme: {url.scheme}")

        return href


class AccessibleItem(Item):
    assets: Dict[str, AccessibleAsset]
    collection: str  # override because default is str | None

    @field_validator("collection")
    def exists(cls, collection):
        validators.collection_exists(collection_id=collection)
        return collection


class StacCollection(Collection):
    id: str
    item_assets: Dict


class Status(str, enum.Enum):
    started = "started"
    queued = "queued"
    failed = "failed"
    succeeded = "succeeded"
    cancelled = "cancelled"


class Ingestion(BaseModel):
    id: str
    status: Status
    message: Optional[str] = None
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    item: Union[Item, Json[Item]]

    @field_validator("created_at", "updated_at", mode="before")
    def set_ts_now(cls, v):
        return v or datetime.now()

    def enqueue(self, db: "services.Database"):
        self.status = Status.queued
        return self.save(db)

    def cancel(self, db: "services.Database"):
        self.status = Status.cancelled
        return self.save(db)

    def save(self, db: "services.Database"):
        self.updated_at = datetime.now()
        db.write(self)
        return self

    def dynamodb_dict(self):
        """DynamoDB-friendly serialization"""
        # convert to dictionary
        output = self.model_dump(exclude={"item"})

        # add STAC item as string
        output["item"] = self.item.model_dump_json()

        # make JSON-friendly (will be able to do with Pydantic V2, https://github.com/pydantic/pydantic/issues/1409#issuecomment-1423995424)
        return jsonable_encoder(output)


@dataclasses.dataclass
class ListIngestionRequest:
    status: Status = Status.queued
    limit: Optional[PositiveInt] = None
    next: Optional[str] = None

    def __post_init_post_parse__(self) -> None:
        # https://github.com/tiangolo/fastapi/issues/1474#issuecomment-1049987786
        if self.next is None:
            return

        try:
            self.next = json.loads(base64.b64decode(self.next))
        except (UnicodeDecodeError, binascii.Error) as e:
            raise RequestValidationError(
                [
                    error_wrappers.ErrorWrapper(
                        ValueError(
                            "Unable to decode next token. Should be base64 encoded JSON"
                        ),
                        "query.next",
                    )
                ]
            ) from e


class ListIngestionResponse(BaseModel):
    items: List[Ingestion]
    next: Optional[str]

    @field_validator("next", mode="before")
    def b64_encode_next(cls, next):
        """
        Base64 encode next parameter for easier transportability
        """
        if isinstance(next, dict):
            return base64.b64encode(json.dumps(next).encode())
        return next


class UpdateIngestionRequest(BaseModel):
    status: Optional[Status] = None
    message: Optional[str] = None
