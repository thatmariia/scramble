from pydantic.dataclasses import dataclass as pyd_dataclass
from pydantic import BaseModel
from typing import TypeVar, Type, Callable, Any, cast
from scramble.utils import Serializable
from scramble.core import (
    Court,
    Player,
    Team,
    Match,
    Round,
    HistoryManager,
)
from scramble.app import AppSession

DomainT = TypeVar("DomainT", bound=Serializable)


def make_dto(domain_cls: Type[DomainT]) -> Type[DomainT]:
    """
    Return a new class (data transfer object) that:
    - inherits *fields* from the domain dataclass
    - behaves like a Pydantic model (validation, .model_dump, etc.)
    - keeps the original to_dict / from_dict contract
    """
    dto_base = cast(Type[DomainT], type(f'{domain_cls.__name__}DTO', (domain_cls,), {}))
    dto_cls = cast(Type[DomainT], pyd_dataclass(dto_base))

    # bridge to_dict / from_dict so Serializable stays happy
    def _to_dict(self) -> dict:
        return self.model_dump(mode="python")  # uses .__dict__

    def _from_dict(cls, data: dict):
        return cls(**data)

    def _to_domain(self) -> DomainT:
        return domain_cls.from_dict(self.to_dict())

    def _from_domain(cls, domain_obj: Serializable):
        return cls(**domain_obj.to_dict())

    dto_cls.to_dict = _to_dict
    dto_cls.from_dict = classmethod(_from_dict)
    dto_cls.to_domain = _to_domain
    dto_cls.from_domain = classmethod(_from_domain)

    return cast(Type[DomainT], dto_cls)


CourtDTO = make_dto(Court)
PlayerDTO = make_dto(Player)
TeamDTO = make_dto(Team)
MatchDTO = make_dto(Match)
RoundDTO = make_dto(Round)
HistoryManagerDTO = make_dto(HistoryManager)

AppSessionDTO = make_dto(AppSession)


class PlayerListDTO(BaseModel):
    active: list[PlayerDTO]
    resting: list[PlayerDTO]
