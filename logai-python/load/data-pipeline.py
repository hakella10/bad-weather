import os
import time

#Data Loaders
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.github import GithubClient,GithubRepositoryReader
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
#Indices and Storage
import pymongo
from llama_index.storage.kvstore.mongodb import MongoDBKVStore as MongoDBCache
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
#Pipeline
from llama_index.core.ingestion import IngestionPipeline, IngestionCache, DocstoreStrategy
#Vector Embedding Model
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

print('Initialize')
MONGODB_URL          = os.getenv('MONGODB_URL')
MONGODB_DBNAME       = os.getenv('MONGODB_DBNAME')
MONGODB_CLIENT       = pymongo.MongoClient(MONGODB_URL)
MONGODB_CACHE        = IngestionCache(cache=MongoDBCache(mongo_client=MONGODB_CLIENT, db_name = MONGODB_DBNAME))
MONGODB_DOCSTORE     = MongoDocumentStore.from_uri(uri=MONGODB_URL, db_name = MONGODB_DBNAME)

GITREPO_TOKEN        = os.getenv('GITREPO_TOKEN')
GITREPO_OWNER        = os.getenv('GITREPO_OWNER')
GITREPO_NAME         = os.getenv('GITREPO_NAME')
GITREPO_BRANCH       = os.getenv('GITREPO_BRANCH')

SPRINGBOOT_GUIDE_PDF = os.getenv('SPRINGBOOT_GUIDE_PDF')
LOGS_DIR             = os.getenv('LOGS_DIR')

EMBED_MODEL          = 'BAAI/bge-small-en-v1.5'
EMBEDDINGS           = HuggingFaceEmbedding(model_name=EMBED_MODEL)

print('->Ingestion Data Sources:')
print('  LOGS_DIR(SimpleDirectoryReader)  = '+LOGS_DIR)
print('  DEV GUIDE(PDFReader)             = '+SPRINGBOOT_GUIDE_PDF)
print('  GITREPO(GithubRepositoryReader)  = github.com/'+GITREPO_OWNER+'/'+GITREPO_NAME,'->',GITREPO_BRANCH)
print('->Embedding Model:')
print('  HuggingFaceEmbedding','->',EMBED_MODEL)
print('->Storage:')
print('  MongoDB','->',MONGODB_DBNAME)

def ingest_logs():
  print('->Ingest Logs')
  start         = time.time()
  splitter      = SentenceSplitter(chunk_size=180,chunk_overlap=20)
  documents     = SimpleDirectoryReader(LOGS_DIR,
                                        filename_as_id = True).load_data()
  pipeline      = IngestionPipeline(
                        transformations   = [splitter,EMBEDDINGS],
                        vector_store      = MongoDBAtlasVectorSearch(
                                              mongodb_client  = MONGODB_CLIENT,
                                              db_name         = MONGODB_DBNAME,
                                              collection_name = 'logs_collection',
                                              index_name      = 'logs_idx'),
                        cache             = MONGODB_CACHE,
                        docstore          = MONGODB_DOCSTORE,
                        docstore_strategy = DocstoreStrategy.UPSERTS,
                  )
  nodes         = pipeline.run(documents = documents)
  end           = time.time()
  print(f'  Total Time = {end-start}', f'Total Documents = {len(documents)}', f'Total Nodes = {len(nodes)}')

def ingest_gitrepo():
  print('->Ingest GitRepo')
  start         = time.time()
  github_client = GithubClient(GITREPO_TOKEN)
  splitter      = SentenceSplitter(chunk_size=400,chunk_overlap=20)
  documents     = GithubRepositoryReader(github_client = github_client,
                                         owner         = GITREPO_OWNER,
                                         repo          = GITREPO_NAME).load_data(branch = GITREPO_BRANCH)
  pipeline      = IngestionPipeline(
                        transformations   = [splitter,EMBEDDINGS], 
                        vector_store      = MongoDBAtlasVectorSearch(
                                              mongodb_client  = MONGODB_CLIENT,
                                              db_name         = MONGODB_DBNAME,
                                              collection_name = 'code_collection',
                                              index_name      = 'code_idx'),
                        cache             = MONGODB_CACHE,
                        docstore          = MONGODB_DOCSTORE,
                        docstore_strategy = DocstoreStrategy.UPSERTS,
                  )
  nodes         = pipeline.run(documents = documents)
  end           = time.time()
  print(f'  Total Time = {end-start}', f'Total Documents = {len(documents)}', f'Total Nodes = {len(nodes)}')

def ingest_devguide():
  print('->Ingest Dev Guide')
  start         = time.time()
  documents     = PDFReader().load_data(file=SPRINGBOOT_GUIDE_PDF)
  pipeline      = IngestionPipeline(
                        transformations   = [EMBEDDINGS], 
                        vector_store      = MongoDBAtlasVectorSearch(
                                              mongodb_client  = MONGODB_CLIENT,
                                              db_name         = MONGODB_DBNAME,
                                              collection_name = 'devguide_collection',
                                              index_name      = 'devguide_idx'),
                        cache             = MONGODB_CACHE,
                        docstore          = MONGODB_DOCSTORE,
                        docstore_strategy = DocstoreStrategy.UPSERTS,
                  )
  nodes         = pipeline.run(documents = documents)
  end           = time.time()
  print(f'  Total Time = {end-start}', f'Total Documents = {len(documents)}', f'Total Nodes = {len(nodes)}')

ingest_logs()
ingest_gitrepo()
ingest_devguide()

print('Manually create atlas vector search index:','logs_idx','code_idx','devguide_idx')