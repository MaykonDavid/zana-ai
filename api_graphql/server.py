# graphql/server.py

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from api_graphql.queries import Query

# Cria o schema unindo os Types e Queries
schema = strawberry.Schema(query=Query)

# Cria o app FastAPI
app = FastAPI(title="Zana AI — GraphQL API")

# Monta o GraphQL no caminho /graphql
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"status": "Zana AI GraphQL rodando! 🌾"}