from fastapi import FastAPI, HTTPException
import openai
import weaviate
import os

app = FastAPI()

# Configuration using environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
openai.api_key = OPENAI_API_KEY

# Initialize Weaviate client
client = weaviate.Client(url=WEAVIATE_URL)

# Define a schema for the Article class
schema = {
    "classes": [{
        "class": "Article",
        "description": "A scraped article with metadata, summary, and embedding.",
        "properties": [
            {"name": "url", "dataType": ["string"]},
            {"name": "title", "dataType": ["string"]},
            {"name": "summary", "dataType": ["text"]},
            {"name": "content", "dataType": ["text"]},
        ]
    }]
}

# Create the schema if not present
if not client.schema.exists():
    client.schema.create(schema)

def get_embedding(text: str) -> list:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
    return embedding

@app.post("/process/")
async def process_data(item: dict):
    try:
        text = item.get("content")
        if not text:
            raise HTTPException(status_code=400, detail="Missing content")
        
        # Get summary from LLM (using GPT-4 as an example)
        summary_resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Summarize this: {text}"}]
        )
        summary = summary_resp["choices"][0]["message"]["content"]

        # Get embedding for the content
        embedding = get_embedding(text)

        # Prepare the document object
        article_obj = {
            "url": item.get("url"),
            "title": item.get("title"),
            "summary": summary,
            "content": text,
        }

        # Store in Weaviate with vector embedding
        client.data_object.create(
            data_object=article_obj,
            class_name="Article",
            vector=embedding
        )
        return {"message": "Article processed and stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
