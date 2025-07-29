from mobio.libs.olap import SingletonArgs
from sqlalchemy import create_engine
from threading import Thread
from time import sleep
import requests
import re
from prometheus_client.parser import text_string_to_metric_families
import gc


class EngineRole:
    LEADER = "LEADER"
    FOLLOWER = "FOLLOWER"


class Engines(metaclass=SingletonArgs):
    # ENGINE config
    ENGINE_ECHO: bool = False
    ENGINE_FUTURE: bool = True

    # ENGINE parameters
    ROLE = "role"
    ENGINE = "engine"
    ALIVE = "alive"

    # FUNCTION parameters
    POOL_NAME = None
    USER_NAME = None
    PASS_WORD = None
    DATABASE = None
    QUERY = None

    dict_shards = {}

    def __init_shard__(self, role, alive, host: str, port: str):
        return {
            self.ROLE: role,
            self.ALIVE: alive,
            self.ENGINE: create_engine(
                self.build_query(host=host, port=int(port)),
                echo=self.ENGINE_ECHO,
                pool_pre_ping=True,
                pool_recycle=3600,
                # future=self.ENGINE_FUTURE,
            ),
        }

    def build_query(self, host: str, port: int):
        return f"{self.POOL_NAME}://{self.USER_NAME}:{self.PASS_WORD}@{host}:{port}/{self.DATABASE}?{self.QUERY if self.QUERY else ''}"

    def __init__(self, uri, sniff=False):
        pattern = re.compile(
            r"""(?P<name>[\w\+]+)://
                        (?:
                            (?P<username>[^:/]*)
                            (?::(?P<password>[^@]*))?
                        @)?
                        (?P<host_port>[^/]*)?
                        (?:/(?P<database>[^\?]*))?
                        (?:\?(?P<query>.*))?""",
            re.X,
        )

        m = pattern.match(uri)
        if m is not None:
            components = m.groupdict()
            self.POOL_NAME = components.get("name")
            self.USER_NAME = components.get("username")
            self.PASS_WORD = components.get("password")
            self.DATABASE = components.get("database")
            self.QUERY = components.get("query")
            for host in components["host_port"].split(","):
                host, port = host.split(":")
                self.dict_shards[host] = self.__init_shard__(
                    role=None, alive=None, host=host, port=port
                )
            if sniff:
                t = Thread(target=self.__sniff__)
                t.daemon = True
                t.start()
        else:
            raise Exception("Could not parse URL from string '%s'" % uri)

    def __sniff__(self):
        while True:
            try:
                lst_host = []
                response = requests.get(
                    "http://db-watcher-service.mobio-olap.svc.cluster.local:8080/metrics",
                    timeout=3,
                )
                metrics = text_string_to_metric_families(response.text)
            except Exception as ex:
                print("ERROR call db-watcher: {}".format(ex))
                metrics = []
                lst_host = []
            if metrics:
                for metric in metrics:
                    for sample in metric.samples:
                        if sample.name == "starrocks_fe_node_alived":
                            lst_host.append(sample.labels.get("IP"))
                            if sample.labels.get("IP") not in self.dict_shards:
                                self.dict_shards[
                                    sample.labels.get("IP")
                                ] = self.__init_shard__(
                                    role=sample.labels.get("Role"),
                                    alive=True if sample.value == 1.0 else False,
                                    host=sample.labels.get("IP"),
                                    port=sample.labels.get("QUERY_PORT", "9030"),
                                )
                            else:
                                self.dict_shards[sample.labels.get("IP")][
                                    self.ROLE
                                ] = sample.labels.get("Role")
                                self.dict_shards[sample.labels.get("IP")][
                                    self.ALIVE
                                ] = (True if sample.value == 1.0 else False)

                for i in list(self.dict_shards):
                    if i not in lst_host:
                        self.dict_shards.pop(i)
                        print("host: {} not exists in database".format(i))
            gc.collect()
            sleep(5)
