from sqlalchemy.orm import Session, sessionmaker
import random
from sqlalchemy.sql import Update, Delete
from mobio.libs.olap import SingletonArgs
from mobio.libs.olap.mining_warehouse.base_engine.engines import Engines, EngineRole


class RoutingSession(Session):
    def __init__(
        self,
        bind=None,
        autoflush=True,
        future=False,
        expire_on_commit=True,
        autocommit=False,
        twophase=False,
        binds=None,
        enable_baked_queries=True,
        info=None,
        query_cls=None,
        dict_shards=None,
    ):
        super().__init__(
            bind=bind,
            autoflush=autoflush,
            future=future,
            expire_on_commit=expire_on_commit,
            autocommit=autocommit,
            twophase=twophase,
            binds=binds,
            enable_baked_queries=enable_baked_queries,
            info=info,
            query_cls=query_cls,
        )
        self.dict_shards = dict_shards

    dict_shards = None

    def get_bind(self, mapper=None, clause=None):
        engine = None
        if self._name:
            for key in list(self.dict_shards):
                value = self.dict_shards.get(key)
                if value:
                    engine = value.get(Engines.ENGINE)
                    break
        if self._flushing or isinstance(clause, (Update, Delete)):
            for key in list(self.dict_shards):
                value = self.dict_shards.get(key)
                if value and value.get(Engines.ROLE) == EngineRole.LEADER:
                    engine = value.get(Engines.ENGINE)
                    break
            if not engine:
                for key in list(self.dict_shards):
                    value = self.dict_shards.get(key)
                    if value and (
                        (
                            value.get(Engines.ROLE) == EngineRole.FOLLOWER
                            and value.get(Engines.ALIVE) is True
                        )
                        or (
                            value.get(Engines.ROLE) is None
                            and value.get(Engines.ALIVE) is None
                        )
                    ):
                        engine = value.get(Engines.ENGINE)
                        break
        else:
            lst_follower = []
            for key in list(self.dict_shards):
                value = self.dict_shards.get(key)
                if value and (
                    (
                        value.get(Engines.ROLE) == EngineRole.FOLLOWER
                        and value.get(Engines.ALIVE) is True
                    )
                    or (
                        value.get(Engines.ROLE) == EngineRole.LEADER
                        and value.get(Engines.ALIVE) is True
                    )
                    or (
                        value.get(Engines.ROLE) is None
                        and value.get(Engines.ALIVE) is None
                    )
                ):
                    lst_follower.append(value.get(Engines.ENGINE))
            if lst_follower:
                engine = random.choice(lst_follower)
        if not engine:
            raise Exception(
                "engine is None with list connection: {}".format(
                    self.dict_shards.keys()
                )
            )
        return engine

    _name = None

    def using_bind(self, name):
        s = RoutingSession()
        vars(s).update(vars(self))
        s._name = name
        return s


class BaseSession(metaclass=SingletonArgs):
    def __init__(self, olap_uri, sniff=False):
        if not olap_uri:
            raise Exception("OLAP URI is null or empty")
        self.olap_uri = olap_uri

        # TODO check sniff
        current_dict_shards = Engines(uri=self.olap_uri, sniff=sniff).dict_shards
        self.SessionLocal = sessionmaker(
            autocommit=True,
            class_=RoutingSession,
            dict_shards=current_dict_shards,
        )
