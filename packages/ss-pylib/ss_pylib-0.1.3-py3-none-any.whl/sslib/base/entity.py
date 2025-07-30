from sslib.base.dict import DictEx


class Entity(DictEx):
    pass


class EntityWithId(Entity):
    id: int = 0
