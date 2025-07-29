from sqlalchemy.dialects import registry

# registry.register(
#     "mobio+pymysql", "mobio.libs.olap.mining_warehouse.dialect", "MobioDialect"
# )
registry.register("mobio", "mobio.libs.olap.mining_warehouse.dialect", "MobioDialect")
