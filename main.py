import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
import time
load_dotenv()


def show_json(obj):
    print(json.loads(obj.model_dump_json()))


class PrimeMarketApp:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            organization=os.environ.get("OPENAI_ORGANISATION"),
            project=os.environ.get("OPENAI_PROJECT")
        )
        categories = self.client.files.create(file=open('cat.json', "rb"), purpose="assistants")
        self.assistant = self.client.beta.assistants.create(
            name="PrimeMarket",
            tools=[{"type": "file_search"}],
            instructions="""
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
            """,
            model="gpt-4o",
        )
        # show_json(self.assistant)

        self.thread = self.client.beta.threads.create()
        # show_json(self.thread)

    def wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def run(self, pdf_path: str):

        _run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        # show_json(_run)

        run = self.wait_on_run(_run, self.thread)
        # show_json(run)

        file = self.client.files.create(file=open(pdf_path, "rb"), purpose="assistants")

        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f"execute {file.id}"
        )
        # show_json(message)


        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        show_json(messages)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Application to identify invoices and statements")
    parser.add_argument(
        "--pdf_path",
        type=str,
        required=True,
        help="The path to the pdf file"
    )
    args = parser.parse_args()
    PrimeMarketApp().run(args.__dict__.get('pdf_path'))
