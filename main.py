from rag_manager import RAG

NEW_DATA_PATH = "/Users/good.jar/Desktop/whispered_amy/text/new"
OLD_DATA_PATH = "/Users/good.jar/Desktop/whispered_amy/text/processed"
TOP_N = 10
COLLECTION_NAME = "Amy_v151"

Athena = RAG(
    private_path = os.path.join(os.getcwd(),"private"),
    collection_name = COLLECTION_NAME
)

Athena.chroma_update()

print(Athena.process_query("How do I maintain my 4.0 GPA?", 10))