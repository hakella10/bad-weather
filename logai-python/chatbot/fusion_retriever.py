import os
import pymongo 
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.retrievers import VectorIndexRetriever,QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.chat_engine import CondenseQuestionChatEngine


MONGODB_URL          = os.getenv('MONGODB_URL')
MONGODB_DBNAME       = os.getenv('MONGODB_DBNAME')
MONGODB_CLIENT       = pymongo.MongoClient(MONGODB_URL)

EMBED_MODEL          = 'BAAI/bge-small-en-v1.5'
EMBEDDINGS           = HuggingFaceEmbedding(model_name=EMBED_MODEL)
Settings.embed_model = EMBEDDINGS

def get_chat_engine(model):
  llm_model            = Ollama(base_url='http://localhost:11434',model=model,request_timeout=300.0)
  Settings.llm         = llm_model
  collections          = ['logs_collection','code_collection','devguide_collection']
  indices              = ['logs_idx','code_idx','devguide_idx']
  retrievers           = []
  for r in range(len(collections)):
    vector_store         = MongoDBAtlasVectorSearch(
                               mongodb_client       = MONGODB_CLIENT,
                               db_name              = MONGODB_DBNAME,
                               collection_name      = collections[r],
                               index_name           = indices[r])
    store_index          = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=EMBEDDINGS)
    index_retriever      = VectorIndexRetriever(index=store_index,similarity_top_k=4)
    retrievers.append(index_retriever)
  fusion_retriever       = QueryFusionRetriever(
                               retrievers,
                               similarity_top_k = 4,
                               llm              = llm_model,
                               num_queries      = 1,
                               verbose          = False)
  response_synthesizer = get_response_synthesizer(llm=llm_model)
  query_engine         = RetrieverQueryEngine(
                               retriever            = fusion_retriever,
                               response_synthesizer = response_synthesizer,
                               node_postprocessors  = [SimilarityPostprocessor(similarity_cutoff=0.7)])
  chat_engine          = CondenseQuestionChatEngine.from_defaults(
                               query_engine         = query_engine,
                               llm                  = llm_model)
  return chat_engine