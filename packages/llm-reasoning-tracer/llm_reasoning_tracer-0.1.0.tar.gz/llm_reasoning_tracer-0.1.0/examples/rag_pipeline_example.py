import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY")

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA
from cognitive_tracer.tracer import CognitiveTracer

retriever = FAISS.load_local(
    "db/",
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
).as_retriever()

llm = OpenAI(temperature=0, openai_api_key=api_key)
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, verbose=True)

tracer = CognitiveTracer(output_path="traces/trace_rag.json")

query = "Summarize the key economic benefits and sustainability impacts of solar energy in cities."
result = qa.run(query, callbacks=[tracer])
print(result)