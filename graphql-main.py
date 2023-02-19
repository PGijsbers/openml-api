from collections import defaultdict

from flask import Flask
from graphql_server.flask import GraphQLView

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
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

    def filter(self, info, **args):
        class_ = args.get("class_")
        query = class_.get_query(info)
        # breakpoint()
        # session = class_.sesh
        alt_query = select(class_._meta.model)

        for f, v in args.items():
            if f not in ["class_", "sort", "first", "last", "before", "after"]:
                if f == "desc":
                    f = "description"
                if f != "status":
                    alt_query = query.where(getattr(class_._meta.model, f).contains(v))
                    query = query.filter(getattr(class_._meta.model, f).contains(v))
                # else:
                #     current_status = select(DatasetStatus.did, func.max(DatasetStatus.status_date)) \
                #         .group_by(DatasetStatus.did)
                #     super_query = select(DatasetStatus) \
                #         .where(
                #         tuple_(DatasetStatus.did, DatasetStatus.status_date) \
                #             .in_(current_status.scalar_subquery())
                #     )
                #     query = query.filter()

        alt_results = Session(create_engine(database_url)).execute(alt_query).all()
        results = query.all()
        # breakpoint()
        return [t for t, in alt_results]

    extras = defaultdict(dict)
    extras['dataset'] = {
        'status': graphene.String()
    }
    Query = type(
        "Query",
        (graphene.ObjectType,),
        {
            **dict(node=relay.Node.Field()),
            **{
                f"{obj.__name__}": SQLAlchemyConnectionField(
                    obj.connection,
                    **{
                        column if column != "description" else "desc": graphene.String()
                        for column in inspect(obj._meta.model).columns.keys()
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
    q = db_session.query_property()
    # breakpoint()
    Base.query = q  # db_session.query_property()
    # Base.sesh = db_session
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
