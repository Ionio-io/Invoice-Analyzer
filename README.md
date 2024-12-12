# Invoice Processing System

This system processes invoices using AI vision to extract data and generate insightful visualizations. It supports both PDF and image files (PNG format) as input.

![Invoice Analyzer](assets/generated-invoice-data.gif)

Note that this can only process invoices that are one page long. Multiple pages are not supported, yet.

## Features

- PDF and image invoice processing
- AI-powered data extraction using Together API
- JSON data output
- Visualization of invoice trends
- Service amount analysis
- Support for multiple invoice items and services

## Prerequisites

- Python 3.8 or higher
- Together API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Invoice-Analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your Together API key.

## Usage

1. Place your invoices in the `invoices` directory (create if it doesn't exist)
2. Run the script:
```bash
python main.py
```

The script will:
- Process all invoices in the directory
- Generate JSON data for each invoice
- Create visualizations:
  - `invoice_trend.png`: Timeline of invoice amounts
  - `service_amounts.png`: Bar chart of amounts by service type
  - Note: You can change the name of the output files in the `main.py` file.
- Save all extracted data to `invoice_data.json`

## Output

The system generates:
- Structured JSON data for each invoice in the `invoice_data.json` file
- Trend analysis graphs
- Total amounts by service type
- Consolidated invoice data file

## Directory Structure

```
accounting-vlm/
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── invoices/           # Place your invoices here
├── invoice_trend.png   # Generated visualization
├── service_amounts.png # Generated visualization
└── invoice_data.json   # Generated data
```

## License

This project is licensed under the MIT License.
Have fun, go wild!
