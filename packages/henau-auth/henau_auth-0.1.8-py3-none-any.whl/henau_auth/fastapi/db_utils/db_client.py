from typing import List

from peewee import (
    Model,
    CharField,
    TextField,
    DateTimeField,
    DateField,
    TimeField,
    SQL,
    IntegerField,
    ColumnMetadata,
    ForeignKeyField,
)
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from .page import paginate
from .construction import splicing_conditions_dict


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


field_type = {
    "text": TextField,
    "datetime": DateTimeField,
    "timestamp": DateTimeField,
    "tinyint": IntegerField,
    "json": TextField,
    "date": DateField,
    "time": TimeField,
    "varchar": CharField,
    "int": IntegerField,
}


def data_to_attr(column: ColumnMetadata):
    return field_type[column.data_type](
        null=column.null, constraints=[SQL(f"DEFAULT {column.default}")]
    )


def generate_attr(columns: List[ColumnMetadata]):
    attr_dict = {}
    for column in columns:
        attr_dict[column.name] = data_to_attr(column)
    return attr_dict


class DbClient:
    def __init__(self, db: ReconnectMySQLDatabase):
        self.db = db
        self.BaseModel = type(
            "BaseModel",
            (Model,),
            {
                "Meta": type("Meta", (), dict(database=db)),
            },
        )
        self.models = {}

    def add_model(self):
        pass

    def add_all_models(self):
        for table in self.db.get_tables():
            self.models[table] = type(
                table,
                (self.BaseModel,),
                {
                    **generate_attr(self.db.get_columns(table)),
                    "Meta": type("Meta", (), dict(table_name=table)),
                },
            )
        for table in self.db.get_tables():
            for foreign_key in self.db.get_foreign_keys(table):
                setattr(
                    self.models[table],
                    foreign_key.dest_table,
                    ForeignKeyField(
                        column_name=foreign_key.column,
                        field=foreign_key.dest_column,
                        model=self.models[foreign_key.dest_table],
                    ),
                )

    def create_tables(self):
        self.db.create_tables(self.models.values())

    def insert(self):
        pass

    def page_query(self, table_name: str, query: dict = {}):
        model = self.models[table_name]
        sql = splicing_conditions_dict(model, model.select(), query)
        return paginate(sql, page=query.get("page") or 1, size=query.get("size") or 10)

    def create(self, table_name: str, body: dict = {}):
        model = Model(self.models[table_name])
        model.create(**body)

    def update(self, table_name: str, body: dict = {}):
        model = self.models[table_name]
        record = model.get_by_id(body.get("id"))
        for key, value in body.items():
            setattr(record, key, value)
        record.save()
