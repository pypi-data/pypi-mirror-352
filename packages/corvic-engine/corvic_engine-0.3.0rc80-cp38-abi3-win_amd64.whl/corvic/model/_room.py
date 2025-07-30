"""Rooms."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

from corvic import eorm, system
from corvic.model._base_model import BelongsToOrgModel
from corvic.model._defaults import Defaults
from corvic.model._proto_orm_convert import (
    room_delete_orms,
    room_orm_to_proto,
    room_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2

OrgID: TypeAlias = eorm.OrgID
RoomID: TypeAlias = eorm.RoomID
FeatureViewID: TypeAlias = eorm.FeatureViewID


class Room(BelongsToOrgModel[RoomID, models_pb2.Room, eorm.Room]):
    """Rooms contain conversations and tables."""

    @classmethod
    def orm_class(cls):
        return eorm.Room

    @classmethod
    def id_class(cls):
        return RoomID

    @classmethod
    def orm_to_proto(cls, orm_obj: eorm.Room) -> models_pb2.Room:
        return room_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.Room, session: eorm.Session
    ) -> Ok[eorm.Room] | InvalidArgumentError:
        return room_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[RoomID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return room_delete_orms(ids, session)

    @classmethod
    def from_id(
        cls, room_id: RoomID, client: system.Client | None = None
    ) -> Ok[Room] | NotFoundError | InvalidArgumentError:
        client = client or Defaults.get_default_client()
        return cls.load_proto_for(room_id, client).map(
            lambda proto_self: cls(client, proto_self)
        )

    @classmethod
    def from_proto(
        cls, proto: models_pb2.Room, client: system.Client | None = None
    ) -> Room:
        client = client or Defaults.get_default_client()
        return cls(client, proto)

    @classmethod
    def create(
        cls,
        name: str,
        client: system.Client | None = None,
    ):
        client = client or Defaults.get_default_client()
        return cls(
            client,
            models_pb2.Room(
                name=name,
            ),
        )

    @classmethod
    def list(
        cls,
        client: system.Client | None = None,
    ) -> Ok[list[Room]] | InvalidArgumentError | NotFoundError:
        """List rooms that exist in storage."""
        client = client or Defaults.get_default_client()
        return cls.list_as_proto(client).map(
            lambda protos: [cls.from_proto(proto, client) for proto in protos]
        )

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def room_id(self) -> RoomID:
        return RoomID(self.proto_self.id)
