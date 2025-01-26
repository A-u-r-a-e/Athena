from rag_manager import RAG
import os

TOP_N = 10

Athena = RAG(private_path = os.path.join(os.getcwd(),"private"),)

Athena.chroma_update()

print(Athena.process_query("How do I maintain my 4.0 GPA?", TOP_N))