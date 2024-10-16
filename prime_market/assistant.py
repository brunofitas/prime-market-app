from dotenv import load_dotenv
from openai import Client
import os
import json
load_dotenv()

instructions = """
Extract the total amount listed in PDF documents.

# Steps

1. **Identify Key Sections**: Inspect the PDF document for sections that typically contain the total amount. These may include headings like "Total Amount," "Invoice Total," or "Grand Total."
2. **Extract Text**: Use optical character recognition (OCR) or PDF parsing libraries to extract text from the PDF document.
3. **Search for Keywords**: Look for common keywords or phrases associated with totals, such as "Total," "Amount," "Sum," or "Balance Due."
4. **Regex Matching**: Apply regular expressions to identify numeric values that are commonly associated with financial totals, such as digits following currency symbols ($, €, etc.).
5. **Verify Context**: Ensure the extracted number is the actual total by checking its proximity to the identified keywords or common section headings.
6. **Resolve Ambiguities**: If multiple candidates are found, use contextual clues such as higher amounts or final sums to determine the most likely total.

# Output Format

- Provide the extracted total amount as a plain number.
- If applicable, include the currency symbol associated with the total amount.

# Examples

- Input: Extract from a PDF with header "Invoice Total" and line "$123.45".
  - Output: $123.45

- Input: PDF document containing the text "Grand Total: 850.00"
  - Output: 850.00

# Notes

- Handle different formatting styles and currency symbols.
- Consider potential errors in OCR that might affect numeric extraction.
- The document might contain similar numbers; validate your extraction by checking for logical consistency.

"""


class Assistant:

    def __init__(self):
        self.client = Client(
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORG_ID"),
            project=os.environ.get("OPENAI_PROJECT_ID")
        )

    def setup(self):
        vector_store = self.client.beta.vector_stores.create(name="PrimeMarket Docs")
        file_paths = ["documents/categories.json"]
        file_streams = [open(path, "rb") for path in file_paths]
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
        assistant = self.client.beta.assistants.create(
            name="PrimeMarket PDF Reader",
            instructions=instructions,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            model="gpt-4o",
        )

        print(json.loads(assistant.model_dump_json()))


if __name__ == "__main__":
    Assistant().setup()
