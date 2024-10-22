import os
from openai import Client
from dotenv import load_dotenv
load_dotenv()


class FileManager:

    def __init__(self):
        self.client = Client(
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_ID"),
            project=os.environ.get("OPENAI_PROJECT_ID")
        )

    def list_vector_stores(self):
        return self.client.beta.vector_stores.list()

    def delete_vector_store(self, id):
        return self.client.beta.vector_stores.delete(
            vector_store_id=id
        )

    def list_files(self):
        return self.client.files.list()


if __name__ == "__main__":
    client = FileManager()
    vector_stores = client.list_vector_stores()
    for store in vector_stores:
        print(f"Removing store {store.id}")
        try:
            client.delete_vector_store(store.id)
        except Exception as e:
            print(e.__class__, e)

