import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.chroma import ChoromaVectorStore
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

#load
reader = SimpleDirectoryReader(input_files=['Assignment_solve.docx'])
documents = reader.load_data()

#vector store setup
db = chromadb.PersistentClient(path='mentora_chroma_db')
chroma_colection = db.get_or_create_collection('mentora')
vector_store = ChoromaVectorStore(chroma_colection=chroma_colection)

#chunks & embeddings & vector store
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_overlap=0),
        HuggingFaceEmbedding(model_name='BAAI/bge-small-en-v1.5')
    ],
    vector_store=vector_store
)

nodes = pipeline.run(documents=documents)

#create vector store index which act as search engine it make vectors searchable which store in vector db
embed_model = HuggingFaceEmbedding(model_name='BAAI/bge-small-en-v1.5')
index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

#query to llm
llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    temperature=0.7,
    api_key=groq_api_key,
    provider="groq"
)

query_engine = index.as_query_engine(
    llm = llm,
    response_mode = 'tree_summarize',
)
query_engine.query('What is law of demand and law of supply in economics?')