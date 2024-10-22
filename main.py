import os
import shutil
import json
from prime_market.assistant_thread import AssistantThread


if __name__ == "__main__":
    for filename in os.listdir(os.path.join('data', 'invoices')):
        response = AssistantThread().run(pdf_path=os.path.join('data', 'invoices', filename))
        dir_name = os.path.join('var', 'outputs', filename.split('.')[0])
        os.makedirs(dir_name, exist_ok=True)
        shutil.copy(os.path.join('data', 'invoices', filename), os.path.join(dir_name, filename))
        with open(os.path.join(dir_name, 'response.json'), 'w') as file:
            json.dump(response, file, indent=4, ensure_ascii=False)
        print(response)
