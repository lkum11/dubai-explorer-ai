import graphene
from graphene import ObjectType, Field, List, Int, String
from flask import current_app
from app.models import User
from app.graphql.gql_objects import UserType
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.elasticsearch.service import get_es_client
from app.rag.embedder import get_embedding_model
import logging

logger = logging.getLogger(__name__)


class Query(ObjectType):
    users = List(UserType)
    user = Field(UserType, id=Int(required=True))
    
    # Move to seperate file
    askRAG = Field(
        String, 
        query_text=String(required=True), 
        description="Ask a question about Dubai attractions using RAG pipeline."
    )

    def resolve_users(self, info):
        return User.query.all()

    def resolve_user(self, info, id):
        return User.query.get(id)
    
    def resolve_askRAG(self, info, query_text):
        try:
            logger.info(f"askRAG resolver called with query: '{query_text[:60]}'")
            embedder = get_embedding_model()
            client = current_app.openai_client
            es_client = current_app.es_client
            retriever = Retriever(es_client, embedder,index_name="wiki_articles_vector", top_k=3)
            relevant_chunks = retriever.retrieve(query_text=query_text)

            generator = Generator(client=client,model="gpt-4o-mini")
            response = generator.generate(query_text=query_text,retrieved_chunks=relevant_chunks)
            return response
        
        except Exception:
            logger.exception(f"Unexpected exception while generating response for query:{query_text[:60]}")
            return "Internal error occurred while generating response."

schema = graphene.Schema(query=Query)
