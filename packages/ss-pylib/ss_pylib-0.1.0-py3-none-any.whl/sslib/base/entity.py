from sslib.base.dict import DictEx


class Entity(DictEx):
    pass


class EntityWithId(DictEx):
    id: int = 0
