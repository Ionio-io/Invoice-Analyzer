import os, glob, json, base64, tempfile
from rich import print, print_json

from pdf2image import convert_from_path
from together import Together
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))


INVOICE_TO_JSON_PROMPT = """
YOU ARE AN MASTER OF INVOICE PARSING. - YOU ARE AN FINANCIAL EXPERT, YOU EXCEL IN PARSING INVOICES AND CONVERTING THEM INTO JSON.



Basically, look at the image of the invoice given to you and convert it STRICTLY into this json format:


{
    "invoice_number": "1234567890",
    "invoice_date": "2024-01-01",
    "invoice_amount": "1000.00",
    "invoice_currency": "USD",
    "invoice_due_date": "2024-01-31",
    "invoice_status": "PAID",
    "invoice_items": [
        {"description": "Product 1", "quantity": 1, "price": 100.00, "total": 100.00}
    ]
}


It is very important that you do not miss any fields. - AND IT IS EXTREMELY IMPORTANT THAT YOU FOLLOW ONLY THIS JSON FORMAT.


YOU MUST NOT MAKE ANY ASSUMPTIONS. - YOU MUST STRICTLY FOLLOW THE JSON FORMAT.


YOU MUST JUST OUTPUT THE JSON DIRECTLY, NO TEXT BEFORE OR AFTER THE JSON.
DIRECTLY JSON. - OUR SYSTEMS WILL NOT BE ABLE TO PARSE ANY TEXT THAT IS NOT JSON.

NO MARKDOWN, NO TEXT, NO EXPLANATIONS, NO COMMENTS, NO THOUGHTS, NO NOTHING.
ONLY JSON.
"""



def get_pdf_or_image_files(directory: str) -> list[str]:
    pdf_files = glob.glob(os.path.join(directory, "**", "*.pdf"), recursive=True)
    image_files = glob.glob(os.path.join(directory, "**", "*.png"), recursive=True)
    print(f"[bold green]Found {len(pdf_files)} PDF files and {len(image_files)} image files[/bold green]")
    
    
    converted_images = []
    for pdf_file in pdf_files:
        continue
        try:
            # Convert PDF pages to images
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(pdf_file, output_folder=temp_dir)
                # Save each page as an image
                for i, image in enumerate(images):
                    image_path = os.path.join(os.path.dirname(pdf_file), f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{i+1}.png")
                    image.save(image_path, 'PNG')
                    converted_images.append(image_path)
        except Exception as e:
            print(f"Error converting PDF {pdf_file}: {str(e)}")
            continue
    
    image_files.extend(converted_images)
    
    return image_files

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_together_api(image_path: str) -> str:
    print(f"[bold green]Processing {image_path}[/bold green]")
    image_data = encode_image(image_path)
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        messages=[
            {
                "role": "system",
                "content": "IT IS NECESSARY THAT YOU OUTPUT ONLY JSON, NO OTHER TEXT, NO MARKDOWN, NO PREXIT OR SUFFIX. YOU ONLY AND DIRECTLY OUTPUT JSON. You are an expert at parsing invoices and converting them into JSON. You are very good at it. OBEY THE USER'S INSTRUCTIONS. ONLY OUTPUT THE JSON."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": INVOICE_TO_JSON_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}",
                        },
                    },
                ],
            }
        ],
    )
    
    response = response.choices[0].message.content
    
    print(response)
    invoice_data = json.loads(response)
    
    print("[bold green]Invoice data:[/bold green]")
    print_json(data=invoice_data, indent=4)
    
    return invoice_data





if __name__ == "__main__":
    invoice_data = []
    
    images = get_pdf_or_image_files("invoices")
    
    for image in images:
        invoice_data.append(call_together_api(image))
        
    with open("invoice_data.json", "w") as f:
        json.dump(invoice_data, f, indent=4)

    print("[bold]Invoice data has been saved to 'invoice_data.json'[/bold]")
    print(f"[blue]Processed {len(invoice_data)} invoices:[/blue]")
    for i, invoice in enumerate(invoice_data, 1):
        print(f"\nInvoice {i}:")
        print(json.dumps(invoice, indent=2))

    amounts = [float(invoice['invoice_amount'].replace('$','').replace(',','')) for invoice in invoice_data]
    dates = [invoice['invoice_date'] for invoice in invoice_data]
    # Calculate total amount by description
    description_totals = {}
    for invoice in invoice_data:
        for item in invoice['invoice_items']:
            desc = item['description']
            if desc not in description_totals:
                description_totals[desc] = 0
            description_totals[desc] += item['total']
    
    print("\n[bold]Total Amount by Service Type:[/bold]")
    for desc, total in description_totals.items():
        print(f"{desc}: ${total:,.2f}")
    
    plt.figure(figsize=(10,6))
    plt.plot(dates, amounts, marker='o')
    plt.title('Invoice Amounts Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
        
    # Save the plot
    plt.savefig('invoice_trend.png')
    print("\nGraph has been saved as 'invoice_trend.png'")


    # Create a bar chart for amounts by description
    plt.figure(figsize=(10,6))
    plt.bar(description_totals.keys(), description_totals.values())
    plt.title('Total Amount by Service Type')
    plt.xlabel('Service Type')
    plt.ylabel('Amount ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('service_amounts.png')
    print("\nService amounts graph has been saved as 'service_amounts.png'")

