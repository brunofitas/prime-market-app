from dotenv import load_dotenv
from openai import Client
import json
import os
load_dotenv()


class AssistantThread:

    def __init__(self):
        self.client = Client(
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_ID"),
            project=os.environ.get("OPENAI_PROJECT_ID")
        )

    def run(self, pdf_path: str):
        pdf_file = self.client.files.create(
            file=open(pdf_path, "rb"), purpose="assistants"
        )

        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": """
                        Output the $invoice_id, $total, $category_id, $currency and the $category of products from categories.json
                        Output the result in json in this format:
                        {
                            "invoice_id": $invoice_id,
                            "currency": $currency,
                            "total": $total (without the currency),
                            "category": $category,
                            "category_id": $category_id
                        }
                        Do not output anything else but the json object in a string format. 
                        Remove the ```json ... ``` and the line breaks from the output.
                    """,
                    "attachments": [
                        {"file_id": pdf_file.id, "tools": [{"type": "file_search"}]}
                    ],
                }
            ]
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=os.environ.get("OPENAI_ASSISTANT_ID")
        )

        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        message_content = messages[0].content[0].text

        print(json.dumps(json.loads(message_content.value), indent=4))
        # print("\n".join(citations))


if __name__ == "__main__":
    AssistantThread().run(pdf_path="invoices/test.pdf")
