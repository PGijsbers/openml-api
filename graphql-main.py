from collections import defaultdict

import sqlalchemy
from flask import Flask
from graphql_server.flask import GraphQLView

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData, func, not_
from sqlalchemy import inspect, select, tuple_, and_
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from functools import partial
import logging

logging.basicConfig(level=logging.INFO)

mysql_url = "mysql://root:ok@127.0.0.1:3306/openml_expdb"

database_url = mysql_url


def generate_graphql_for(tables):
    # Dynamically generating the auxiliary types detailed in this tutorial:
    # https://docs.graphene-python.org/projects/sqlalchemy/en/latest/tutorial/#schema
    # We use the overloaded `type` function to construct new classes dynamically:
    # https://docs.python.org/3/library/functions.html#type
    # type(name, bases, dict)
    alchemy_classes = [
        type(
            f"{table.__name__}",
            (SQLAlchemyObjectType,),
            dict(
                Meta=type(
                    "Meta",
                    tuple(),
                    dict(
                        model=table,
                        interfaces=(relay.Node,)
                    )
                )
            )
        )
        for table in tables.values()
    ]

    qualities = Session(create_engine(database_url)).execute(select(tables['quality'].name)).all()
    qualities = [q for q, in qualities if q.isalnum()]

    def filter(self, info, **args):
        class_ = args.get("class_")
        query = select(class_._meta.model)

        def create_clause(field, expr):
            if expr.startswith("!"):
                use_not = True
                expr = expr[1:]
            else:
                use_not = False

            if "..." in expr:
                dot_start, dot_end = expr.index("..."), expr.index("...") + 3
                first, last = expr[:dot_start], expr[dot_end:]
                clause = and_(first < field, field < last)
            if expr.startswith("contains:"):
                clause = field.contains(expr[len("contains:"):])
            if expr.startswith("in:"):
                values = expr[len("in:"):].split(",")
                clause = field.in_(values)
            if expr.startswith(">="):
                clause = field >= float(expr[len(">="):])
            if expr.startswith(">"):
                clause = field > float(expr[len(">"):])
            if expr.startswith("<="):
                clause = field <= float(expr[len("<="):])
            if expr.startswith("<"):
                clause = field < float(expr[len("<"):])
            if expr.startswith("="):
                clause = field == expr[len("="):]
            if expr.isalnum():
                clause = field == expr
            if use_not:
                return not_(clause)
            else:
                return clause
            raise RuntimeError(f"{field=}, {expr=}")

            # not sure if want to use regex, e.g.:
            # re.(r"(^=[\w\d]+$|^[\w\d]+=$)")

        for f, v in args.items():
            if f not in ["class_", "sort", "first", "last", "before", "after"]:

                if f == "desc":
                    f = "description"
                if f == "status" and class_._meta.model.__name__ == "dataset":
                    Dataset = tables['dataset']
                    DatasetStatus = tables['dataset_status']
                    current_status = select(DatasetStatus.did, func.max(DatasetStatus.status_date)) \
                        .group_by(DatasetStatus.did)
                    super_query = select(DatasetStatus.did) \
                        .where(
                        and_(
                            tuple_(DatasetStatus.did, DatasetStatus.status_date) \
                                .in_(current_status.scalar_subquery()),
                                DatasetStatus.status == v
                        )
                    )
                    query = query.where(Dataset.did.in_(super_query.scalar_subquery()))
                elif f in qualities and class_._meta.model.__name__ == "dataset":
                    DataQuality = tables['data_quality']
                    clause = create_clause(getattr(DataQuality, "value"), v)
                    matching_datasets = select(DataQuality.data).where(and_(DataQuality.quality_name == f, clause))
                    Dataset = tables['dataset']
                    query = query.where(Dataset.did.in_(matching_datasets.scalar_subquery()))
                else:
                    clause = create_clause(getattr(class_._meta.model, f), v)
                    query = query.where(clause)

        results = Session(create_engine(database_url)).execute(query).all()
        return [t for t, in results]

    extras = defaultdict(dict)
    extras['dataset'] = {
        'status': graphene.String(),
        **{q: graphene.String() for q in qualities}
    }

    # def mysql_to_graphql(type_):
    #     if issubclass(type_, sqlalchemy.sql.sqltypes.Integer):
    #         return graphene.Int()
    #     if issubclass(type_, sqlalchemy.sql.sqltypes.Float):
    #         return graphene.Float()
    #     if issubclass(type_, sqlalchemy.sql.sqltypes.String):
    #         return graphene.String()
    #     if issubclass(type_, sqlalchemy.sql.sqltypes.DateTime):
    #         return graphene.String()
    #     raise KeyError(f"{type_=}")

    Query = type(
        "Query",
        (graphene.ObjectType,),
        {
            **dict(node=relay.Node.Field()),
            **{
                f"{obj.__name__}": SQLAlchemyConnectionField(
                    obj.connection,
                    **{
                        col_name if col_name != "description" else "desc": graphene.String()
                        # mysql_to_graphql(type(column.type))
                        for col_name, column in inspect(obj._meta.model).columns.items()
                    },
                    **extras[obj.__name__]
                )
                for obj in alchemy_classes
            },
            **{
                f"resolve_{obj.__name__}": partial(filter, class_=obj)
                for obj in alchemy_classes
            }
        }
    )
    return graphene.Schema(query=Query)


if __name__ == "__main__":
    # 1. Generate ORM from Database
    engine = create_engine(database_url)

    db_session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    ))

    # throws a name error
    # Base.prepare(autoload_with=engine)
    metadata = MetaData()
    metadata.reflect(
        engine,
    )
    Base = automap_base(metadata=metadata)
    Base.query = db_session.query_property()
    # How do we appropriately use the session with the 2.0 `select` syntax?
    Base.prepare()

    # 2. Generate GraphQL schema from ORM
    graphql_schema = generate_graphql_for(Base.classes)

    # 3. Start a server with GraphQL endpoint
    app = Flask(__name__)
    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view(
            'graphql',
            schema=graphql_schema,
            graphiql=True,
        )
    )

    app.run(host="127.0.0.1", port=8000)
