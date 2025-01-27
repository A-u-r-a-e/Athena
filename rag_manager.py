from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json
import os
import tqdm

class RAG:
    def __init__(self, private_path):

        self.chunk_length = 250*(5+1)
        
        constants =  open(os.path.join(private_path,"constants.json"))
        self.data = json.load(constants)

        self.openaikey = self.data["openai"]
        self.collection_name = self.data["collection_name"]
        self.descriptor = self.data["descriptor"]
        self.rephrase_prompt = self.data["rephraser_descriptor"]

        self.openai_client = OpenAI(api_key=self.openaikey)
        self.embedding_function = OpenAIEmbeddingFunction(api_key=self.openaikey)

        self.chroma_client = chromadb.PersistentClient(path = os.path.join(private_path,"data"))
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name, embedding_function=self.embedding_function)
    
    def load_text_from_file(self, filename, data_path):
        texts = []
        filepath = os.path.join(data_path,filename)
        f = open(filepath, "r")
        chunks = self.chunk_with_padding(f.read(), max_chunk_length=self.chunk_length)
        for idx, chunk in enumerate(chunks):
            texts.append({
                "chunk_id": f"{filename[:-4]}_{idx}",
                "text": chunk,
                "metadata": {
                    "youtube_source": f"https://youtu.be/{filename[:-4]}",
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                }
            })
        return texts

    def chunk_with_padding(self, text, max_chunk_length=4096):
        lines = text.splitlines(keepends=True)
        linecount = len(lines)
        
        # chunk into distinct chunks of at most 10 lines
        chunks = []
        for idx in range(0,linecount,10):
            line = lines[idx]
            character_count = len(line)
            text = line
            for i in range(idx, linecount):
                if i-idx < 10 and character_count + len(lines[i]) < max_chunk_length / 2:
                    character_count += len(lines[i])
                    text += lines[i]
                else:
                    break
            chunks.append(text)
        
        #merge them with one extra start and end chunk
        merged_chunks = [chunks[0]]
        for idx in range(1,len(chunks)):
            merged_chunks.append(chunks[idx-1] + chunks[idx])

        return merged_chunks

    def move_used_data(self, filename, source_path, dest_path):
        source_file = os.path.join(source_path, filename)
        destination_file = os.path.join(dest_path, filename)
        os.rename(source_file,destination_file)

    def chroma_append(self, collection, texts):
        for i, text in tqdm.tqdm(enumerate(texts), total=len(texts)):
            self.collection.add(
                ids=[text["chunk_id"]],
                documents=[text["text"]],
                metadatas=[text["metadata"]]
            )

    def chroma_update(self):
        from_path = self.data["FRESH_DATA_PATH"]
        to_path = self.data["PROCESSED_DATA_PATH"]
        if (len(os.listdir(from_path))>0):
            for filename in tqdm.tqdm(os.listdir(from_path), total=len(os.listdir(from_path))):
                chunked_text = self.load_text_from_file(filename, from_path)
                self.chroma_append(self.collection, chunked_text)
                self.move_used_data(filename, from_path, to_path)

    def find_in_chroma(self, qtext,topQ):
        results = self.collection.query(
            query_texts = qtext,
            include = ["documents", "metadatas", "distances"],
            n_results=topQ
        )
        outputString = ""
        for i in range(len(results["ids"][0])):
            outputString += "Cite the following youtube link if used: " + results["metadatas"][0][i]["youtube_source"] + "\n Transcript Contents: \n" + results["documents"][0][i] + "\n"
        return outputString

    def process_query(self, channel_context, query, topQ):
        rephrased = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.rephrase_prompt},
                {"role": "user", "content": query}
            ]
        )
        
        context = self.find_in_chroma(rephrased.choices[0].message.content, topQ)

        answer = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "system", "content": self.descriptor},
                {"role": "user", "content": f"The conversation so far: {channel_context} \n Most relevant transcript segments from Amy's videos in order: {context} \n Fan/Student Question: Hi Athena! {query}"}
            ]
        )

        return answer.choices[0].message.content