# 1WorldSync Content1 API Python Client

A Python client for interacting with the 1WorldSync Content1 API.

## Installation

```bash
pip install oneworldsync
```

## Key Features

- Authentication with HMAC
- Product fetching by GTIN, GLN, or target market
- Product hierarchy retrieval
- Nutritional information extraction for food/beverage products
- Pagination support
- Comprehensive error handling
- Content1-specific data models
- OpenAPI 3.0.1 specification support
- Command Line Interface (CLI)

## Package Structure

```
oneworldsync/
├── __init__.py           # Package initialization and version
├── content1_client.py    # Main Content1 API client
├── content1_auth.py      # HMAC authentication for Content1 API
├── cli.py               # Command Line Interface
├── models.py            # Data models for API responses
├── exceptions.py        # Custom exceptions
└── utils.py             # Utility functions
```

## Quick Start

### Python API

```python
from oneworldsync import Content1Client

# Initialize the client
client = Content1Client(
    app_id='your_app_id',
    secret_key='your_secret_key',
    gln='your_gln'  # Optional
)

# Count products
count = client.count_products()
print(f"Total products: {count}")

# Fetch products by GTIN
products = client.fetch_products_by_gtin(['00000000000000'])
print(f"Found {len(products.get('items', []))} products")

# Fetch products with criteria
criteria = {
    "targetMarket": "US",
    "fields": {
        "include": ["gtin", "brandName", "gpcCategory"]
    }
}
results = client.fetch_products(criteria)
```

### Command Line Interface

The package installs a command-line tool called `ows` that can be used to interact with the Content1 API:

```bash
# Show version
ows --version

# Show help
ows --help

# Test login credentials
ows login

# Fetch products
ows fetch --gtin 12345678901234 --target-market US
ows fetch --gtin 052000050585 --fields "gtin,gtinName,brandName"
ows fetch --output results.json

# Count products
ows count --target-market EU
ows count --limit 10
ows count --output count.json

# Fetch product hierarchies
ows hierarchy --gtin 12345678901234
ows hierarchy --target-market US --output hierarchy.json
```

The CLI requires credentials to be stored in `~/.ows/credentials` file:
```
ONEWORLDSYNC_APP_ID=your_app_id
ONEWORLDSYNC_SECRET_KEY=your_secret_key
ONEWORLDSYNC_USER_GLN=your_gln  # Optional
ONEWORLDSYNC_CONTENT1_API_URL=https://content1-api.1worldsync.com  # Optional
```

## Authentication

The client supports authentication using your 1WorldSync Content1 API credentials:

```python
# Using parameters
client = Content1Client(
    app_id='your_app_id',
    secret_key='your_secret_key',
    gln='your_gln'  # Optional
)

# Using environment variables
# ONEWORLDSYNC_APP_ID
# ONEWORLDSYNC_SECRET_KEY
# ONEWORLDSYNC_USER_GLN (optional)
# ONEWORLDSYNC_CONTENT1_API_URL (optional)
client = Content1Client()
```

## Examples

See the [examples](examples/) directory for more detailed usage examples:

### Basic Examples
- **content1_example.py**: Basic usage of the Content1 API client to fetch products
- **content1_advanced_example.py**: Advanced usage with date filtering and pagination

### Nutritional Information Examples
- **simple_nutrition_example.py**: Simple example showing how to extract nutritional information
- **django_nutrition_service.py**: Django service for retrieving nutritional information
- **django_food_nutrition_example.py**: Example for food/beverage products with nutritional data

### Key Finding: Nutritional Information Structure
Nutritional information in the Content1 API is found in:
```
item -> nutrientInformation -> nutrientDetail
```

Each nutrient detail contains:
- `nutrientTypeCode`: The type of nutrient (e.g., "ENER-" for calories)
- `quantityContained`: The amount of the nutrient
- `dailyValueIntakePercent`: The percentage of daily value (if applicable)

For more details on nutritional data integration, see [README_nutrition.md](examples/README_nutrition.md).

## Advanced Example

```python
# Create a date range for the last 30 days
today = datetime.datetime.now()
thirty_days_ago = today - datetime.timedelta(days=30)

date_criteria = {
    "lastModifiedDate": {
        "from": {
            "date": thirty_days_ago.strftime("%Y-%m-%d"),
            "op": "GTE"
        },
        "to": {
            "date": today.strftime("%Y-%m-%d"),
            "op": "LTE"
        }
    }
}

# Fetch products with specific fields and sorting
fetch_criteria = {
    "targetMarket": "US",
    "lastModifiedDate": date_criteria["lastModifiedDate"],
    "fields": {
        "include": [
            "gtin", "informationProviderGLN", "targetMarket",
            "lastModifiedDate", "brandName", "gpcCategory"
        ]
    },
    "sortFields": [
        {"field": "lastModifiedDate", "desc": True},
        {"field": "gtin", "desc": False}
    ]
}

# Fetch first page with pagination
products = client.fetch_products(fetch_criteria, page_size=10)

# Handle pagination
if "searchAfter" in products:
    # Use fetch_next_page with original criteria to maintain filters
    next_page = client.fetch_next_page(products, page_size=10, original_criteria=fetch_criteria)
```

## Documentation

For more detailed documentation, see the [docs](docs/) directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.