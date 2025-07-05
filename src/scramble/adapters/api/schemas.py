from pydantic.dataclasses import dataclass as pyd_dataclass
from pydantic import BaseModel
from typing import (
    get_origin, get_args,
    TypeVar, Type, Any,
    Union, Optional, List
)
from types import UnionType
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

_DTO_REGISTRY: dict[type, type] = {}


def _ensure_dto(tp: Any) -> Any:
    """
    Return the DTO version of `tp` (recursively) if it's a Serializable dataclass.
    """
    origin = get_origin(tp)
    args = get_args(tp)

    # handle generics like list[Player]
    if origin in (list, List):
        return List[_ensure_dto(args[0])]

    # handle Optional / Union
    if origin in (Union, UnionType):
        nested = tuple(_ensure_dto(a) for a in args)
        # optional (Union[X, None]) special-case
        if len(nested) == 2 and type(None) in nested:
            real = nested[0] if nested[1] is type(None) else nested[1]
            return Optional[real]
        return Union[nested]

    # plain class
    if isinstance(tp, type) and issubclass(tp, Serializable):
        return make_dto(tp)  # recursive
    return tp


def make_dto(domain_cls: Type[DomainT]) -> Type[DomainT]:
    """
    Creates (recursively) a new class (data transfer object) that:
    - inherits *fields* from the domain dataclass
    - behaves like a Pydantic model (validation, .model_dump, etc.)
    - keeps the original to_dict / from_dict contract
    """
    # Already processed?
    if domain_cls in _DTO_REGISTRY:
        return _DTO_REGISTRY[domain_cls]  # type: ignore[return-value]

    # First ensure *this* domain class is a dataclass itself
    domain_dataclass = pyd_dataclass(domain_cls)   # noop if already decorated

    # build new annotations with nested DTOs swapped in
    new_annots = {
        fld: _ensure_dto(tp)
        for fld, tp in domain_dataclass.__annotations__.items()
    }

    # create the DTO subclass with rewritten annotations
    dto_base = type(
        f"{domain_cls.__name__}DTO",
        (domain_dataclass,),
        {"__annotations__": new_annots},
    )
    dto_cls = pyd_dataclass(dto_base)

    _DTO_REGISTRY[domain_cls] = dto_cls

    # bridge to_dict / from_dict so Serializable stays happy
    def _to_dict(self) -> dict:
        return self.model_dump(mode="python")

    def _from_dict(cls, data: dict):
        return cls(**data)

    # bridge to_domain / from_domain so Pydantic stays happy
    def _to_domain(self) -> DomainT:
        return domain_cls.from_dict(self.to_dict())

    def _from_domain(cls, dom: Serializable):
        return cls(**dom.to_dict())

    dto_cls.to_dict = _to_dict
    dto_cls.from_dict = classmethod(_from_dict)
    dto_cls.to_domain = _to_domain
    dto_cls.from_domain = classmethod(_from_domain)

    return dto_cls


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
