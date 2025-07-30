# Python Iconic API Client

[![PyPI version](https://badge.fury.io/py/py-iconic-api.svg)](https://badge.fury.io/py/py-iconic-api)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC--BY--NC--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/deed.en)

A comprehensive, resource-based Python client for interacting with [The Iconic SellerCenter API](https://sellercenter-api.theiconic.com.au/docs/).

> **Disclaimer:** This is an **unofficial** package and is not affiliated with or endorsed by The Iconic. Use at your own risk.

## Features

- ✨ Intuitive resource-based API design with an object-oriented approach
- 🔄 Both synchronous and asynchronous clients with consistent interfaces
- 🔒 OAuth2 Client Credentials authentication with automatic token management
- 🛡️ Request signing for secure endpoints
- 📊 Type-safe API responses using Pydantic models
- 🌐 Comprehensive API coverage for The Iconic SellerCenter
- 📝 Detailed model definitions and type hints
- 🚦 Built-in rate limiting with Redis support
- 🔄 Automatic pagination handling with multiple access patterns
- 🧠 Smart error handling with retries for rate limits and transient errors

## Installation

```bash
pip install py-iconic-api
```

For Redis-based rate limiting support:

```bash
pip install py-iconic-api[redis]
```

## Authentication

The Iconic API uses OAuth2 Client Credentials flow for authentication. You'll need to obtain a Client ID and Client Secret from The Iconic's SellerCenter.

```python
from iconic_api.client import IconicClient

# Initialize the client
client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)
```

For asynchronous operations:

```python
from iconic_api.client import IconicAsyncClient
import asyncio

async def main():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.sellercenter.com.au"
    )
    
    # Use the client
    # ...
    
    # Close the client when done
    await client.close()

# Run with asyncio
asyncio.run(main())
```

## Resource-Based API

This client implements a resource-based design that makes working with the API intuitive:

```python
# Get a product set by ID
product_set = client.product_sets.get(123)

# Access properties directly
print(f"Product Set: {product_set.name} (${product_set.price})")

# Get all products within this product set
products = product_set.get_products()

# Create a new product in the set
new_product = product_set.create_product({
    "seller_sku": "MY-PRODUCT-001",
    "variation": "M",
    "status": "active",
    "name": "Example Product - Medium"
})

# Update stock for a product
new_product.update_stock(quantity=100)
```

## Examples

### Product Management

#### Basic Product Set Creation

```python
from iconic_api.client import IconicClient
from iconic_api.models import CreateProductSetRequest

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Create a simple product set using the request model
create_request = CreateProductSetRequest(
    name="Basic T-Shirt",
    price=29.99,
    seller_sku="TS-BASIC-001",
    brand_id=123,  # Use an actual brand ID
    primary_category_id=456,  # Use an actual category ID
    description="Basic cotton t-shirt, perfect for everyday wear",
    attributes={
        "10001": "Cotton",  # Example attribute ID and value
        "10002": 12345      # Another example attribute ID and value
    }
)

product_set = client.product_sets.create_product_set(create_request)
print(f"Created product set with ID: {product_set.id}")

# Add a simple product variant
product = product_set.create_product({
    "seller_sku": "TS-BASIC-001-M",
    "variation": "M",
    "status": "active",
    "name": "Basic T-Shirt - Medium"
})
print(f"Created product variant: {product.name} (ID: {product.id})")
```

#### Comprehensive Product Creation

```python
from iconic_api.client import IconicClient
from datetime import datetime, timedelta

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# First, let's find a brand and category to use
# Get a brand by name (partial match)
brands = client.brands.list(name="example")
if not brands:
    print("No matching brands found. Please create one first.")
    exit()
brand = brands[0]

# Get a category that matches our product type
categories = client.categories.list()
apparel_categories = [c for c in categories if 'apparel' in c.name.lower()]
if not apparel_categories:
    print("No apparel categories found. Please use a valid category.")
    exit()
category = apparel_categories[0]

# Get the attribute set for this category to understand required attributes
attribute_set_id = category.attributeSetId
attribute_set = client.attribute_sets.get_attribute_set(attribute_set_id)
attributes = attribute_set.get_attributes()

# Create an AttributeHelper to simplify working with attributes
from iconic_api.resources.attribute_helper import AttributeHelper
helper = AttributeHelper(attribute_set)

# Prepare attribute values using attribute names instead of IDs
attribute_values = {
    "Color": "Blue",
    "Size": "M",
    "Material": "Cotton",
    "Pattern": "Solid",
    "Condition": "New",
    "Gender": "Unisex"
}

# Create a comprehensive product set with prepared attributes
product_set = client.product_sets.create_product_set({
    "name": "Premium Cotton T-Shirt",
    "price": 39.99,
    "seller_sku": "TS-PREMIUM-001",
    "brand_id": brand.id,
    "primary_category_id": category.id,
    "description": "Premium quality cotton t-shirt with a soft feel and durable construction.",
    "attribute_values": attribute_values  # The helper will process these
})

print(f"Created product set with ID: {product_set.id}")

# Set up sale pricing for the product set
sale_start = datetime.now()
sale_end = sale_start + timedelta(days=30)

# Add products (variations) to the product set
sizes = ["S", "M", "L", "XL"]
for size in sizes:
    product = product_set.create_product({
        "seller_sku": f"TS-PREMIUM-001-{size}",
        "variation": size,
        "status": "active",
        "name": f"Premium Cotton T-Shirt - {size}"
    })
    
    # Set initial stock for this product
    quantity = 50  # Example quantity
    product.update_stock(quantity)
    
    print(f"Created product {product.name} with ID {product.id} and set stock to {quantity}")

# Upload product images (if you have image files)
try:
    product_set.upload_image("path/to/front_image.jpg", position=1)
    product_set.upload_image("path/to/back_image.jpg", position=2)
    product_set.upload_image("path/to/model_image.jpg", position=3)
except Exception as e:
    print(f"Error uploading images: {e}")

# Add the product set to a product group for organization
product_set.add_to_group({"name": "Premium Apparel"})

client.close()
```

#### Updating Products

```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Fetch an existing product set
product_set_id = 123  # Replace with actual ID
product_set = client.product_sets.get(product_set_id)

# Update product set details
product_set.update_product_set({
    "name": f"{product_set.name} - Updated",
    "description": "Updated description with more details about the product.",
    "attribute_values": {
        "Color": "Red",  # Update an attribute
        "Style": "Casual"  # Add a new attribute
    }
})

# Update a specific product in the set
products = product_set.get_products()
if products:
    product = products[0]
    
    # Update basic product details
    product.update({
        "seller_sku": f"{product.sellerSku}-UPDATED",
        "name": f"{product.name} - Updated"
    })
    
    # Update product status
    product.update_status("inactive")
    
    # Update product price for a specific country
    product.update_price(
        country="AU",
        price=49.99,
        sale_price=39.99,
        status="active"
    )

client.close()
```

### Inventory Management

#### Bulk Stock Updates

```python
from iconic_api.client import IconicClient
from iconic_api.models.stock import StockUpdateRequest, StockUpdateItem

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Method 1: Update stock for multiple products in a single request (max 100 products)
products_to_update = [
    {"productId": 1001, "quantity": 50},
    {"productId": 1002, "quantity": 75},
    {"productId": 1003, "quantity": 100}
]

# The API limits to 100 products per update, so chunk them if needed
def update_stock_in_chunks(items, chunk_size=100):
    """Update stock in chunks to respect API limits."""
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        result = client.stock.update_stock(chunk)
        print(f"Updated {len(result)} products in chunk {i//chunk_size + 1}")

# Update stock in chunks
update_stock_in_chunks(products_to_update)

# Method 2: Using StockUpdateRequest model
update_request = StockUpdateRequest(
    items=[
        StockUpdateItem(productId=1004, quantity=60),
        StockUpdateItem(productId=1005, quantity=30),
    ]
)
client.stock.update_stock(update_request)

# Method 3: Update stock for all products in a product set
product_set_id = 123  # Replace with actual ID
product_set = client.product_sets.get(product_set_id)
products = product_set.get_products()

# Get current stock levels
stock_data = product_set.get_product_stocks()
stock_dict = {item.product_id: item.quantity for item in stock_data if item.product_id}

# Prepare updates (e.g., increase all stock by 10%)
stock_updates = [
    {"productId": product.id, "quantity": int(stock_dict.get(product.id, 0) * 1.1)}
    for product in products
]

# Update in chunks
update_stock_in_chunks(stock_updates)

client.close()
```

#### Asynchronous Bulk Stock Updates

For large inventory updates, using the asynchronous client can be more efficient:

```python
import asyncio
from iconic_api.client import IconicAsyncClient

async def update_inventory():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.sellercenter.com.au"
    )
    
    # Fetch product IDs to update
    # This could come from a CSV file, database, or other source
    product_updates = [
        {"productId": 1001, "quantity": 50},
        {"productId": 1002, "quantity": 75},
        # ... more products
        {"productId": 1099, "quantity": 25},
    ]
    
    # Split into chunks of 100 (API limit)
    chunks = [product_updates[i:i+100] for i in range(0, len(product_updates), 100)]
    
    # Create tasks for concurrent updates
    tasks = [client.stock.update_stock_async(chunk) for chunk in chunks]
    
    # Execute all update tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Process results
    total_updated = sum(len(result) for result in results)
    print(f"Updated stock for {total_updated} products")
    
    await client.close()

# Run the async function
asyncio.run(update_inventory())
```

### Order Management

#### Listing and Filtering Orders

```python
from iconic_api.client import IconicClient
from iconic_api.models import ListOrdersRequest
from datetime import datetime, timedelta

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Get orders from the last 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)

# Method 1: Using keyword arguments
recent_orders = client.orders.list(
    date_start=thirty_days_ago.date(),
    date_end=datetime.now().date(),
    status="pending",
    limit=50
)

print(f"Found {len(recent_orders)} pending orders in the last 30 days")

# Method 2: Using request model for more complex filters
request = ListOrdersRequest(
    date_start=thirty_days_ago.date(),
    date_end=datetime.now().date(),
    section="pending",  # Filter by order status
    shipment_type="express",  # Filter by shipment type
    limit=50,
    outlet=False,  # Exclude outlet orders
    invoice_required=True  # Only orders requiring invoices
)

filtered_orders = client.orders.list_orders(**request.model_dump())
print(f"Found {len(filtered_orders)} orders matching complex criteria")

# Get all orders using pagination
all_orders = client.orders.paginate_all(
    date_start=thirty_days_ago.date(),
    date_end=datetime.now().date()
)
print(f"Total orders in the last 30 days: {len(all_orders)}")

client.close()
```

#### Updating Order Status

```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Get a specific order by number
order_number = "12345678"  # Replace with actual order number
order = client.orders.get_by_order_number(order_number)
print(f"Current status of order {order_number}: {order.status}")

# Mark the order as packed (ready for shipment)
updated_order = order.mark_as_packed()
print(f"Updated status: {updated_order.status}")

# Update the shipment information when shipped
order.update_shipment(
    tracking_number="TRACK123456789",
    shipping_provider="Australia Post",
    shipping_type="Express"
)
print(f"Order marked as shipped with tracking: TRACK123456789")

# Update order status (e.g., to cancel an order)
try:
    order.cancel(reason="Customer requested cancellation")
    print("Order has been cancelled")
except Exception as e:
    print(f"Error cancelling order: {e}")

client.close()
```

#### Importing Orders to External Systems

```python
from iconic_api.client import IconicClient
import csv
from datetime import datetime, timedelta

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Export orders to a CSV file for import into another system
def export_orders_to_csv(orders, filename):
    """Export orders to a CSV file for external systems."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'OrderNumber', 'OrderDate', 'PaymentMethod', 'Status',
            'CustomerName', 'CustomerEmail', 'Address', 'City',
            'State', 'PostalCode', 'Country', 'ShippingMethod',
            'ProductSKU', 'ProductName', 'Quantity', 'Price', 'TotalAmount'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for order in orders:
            # Get order details with items
            order_details = client.orders.get_by_order_number(order.orderNumber)
            
            # Basic order information
            order_info = {
                'OrderNumber': order_details.orderNumber,
                'OrderDate': order_details.createdAt,
                'PaymentMethod': order_details.paymentMethod,
                'Status': order_details.status,
                'CustomerName': f"{order_details.customerFirstName} {order_details.customerLastName}",
                'CustomerEmail': order_details.customerEmail,
                'Address': order_details.deliveryAddress,
                'City': order_details.deliveryCity,
                'State': order_details.deliveryState,
                'PostalCode': order_details.deliveryPostCode,
                'Country': order_details.deliveryCountry,
                'ShippingMethod': order_details.shippingMethod,
            }
            
            # Write a row for each item in the order
            for item in order_details.items:
                row = order_info.copy()
                row.update({
                    'ProductSKU': item.sellerSku,
                    'ProductName': item.name,
                    'Quantity': item.quantity,
                    'Price': item.price,
                    'TotalAmount': order_details.price
                })
                writer.writerow(row)

# Get orders from last 7 days
seven_days_ago = datetime.now() - timedelta(days=7)
recent_orders = client.orders.list(
    date_start=seven_days_ago.date(),
    date_end=datetime.now().date(),
    status="pending"
)

# Export to CSV
export_orders_to_csv(recent_orders, "pending_orders_export.csv")
print(f"Exported {len(recent_orders)} orders to pending_orders_export.csv")

client.close()
```

### Working with Other Resources

#### Brands

```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# List all brands
brands = client.brands.list()
print(f"Found {len(brands)} brands")

# Get a specific brand
brand = client.brands.get(123)  # Replace with actual brand ID
print(f"Brand: {brand.name}")

# Get brand attributes
attributes = brand.get_attributes()
print(f"Brand has {len(attributes)} attributes")

# Get product sets for this brand
product_sets = brand.get_product_sets(limit=10)
print(f"Brand has {len(product_sets)} product sets")

client.close()
```

#### Categories

```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Get the category tree
category_tree = client.categories.get_tree()
print(f"Found {len(category_tree)} top-level categories")

# Get a specific category
category = client.categories.get(123)  # Replace with actual category ID
print(f"Category: {category.name}")

# Get category attributes
attributes = category.get_attributes()
print(f"Category has {len(attributes)} attributes")

# Get child categories
children = category.get_children()
print(f"Category has {len(children)} direct child categories")

# Get product sets in this category
product_sets = category.get_product_sets(limit=10)
print(f"Category has {len(product_sets)} product sets")

client.close()
```

#### Financial Transactions

```python
from iconic_api.client import IconicClient
from datetime import datetime, timedelta

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Get financial statements
statements = client.finance.list_statements(
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now(),
    paid=True,
    country="AU"
)
print(f"Found {len(statements)} financial statements")

# Get current statement
current_statement = client.finance.get_current_statement(country="AU")
print(f"Current statement ID: {current_statement.id}")

# Get statement details
statement_details = client.finance.get_statement_details(current_statement.id)
print(f"Statement total amount: {statement_details.totalAmount}")

# Get transactions
transactions = client.finance.list_transactions(
    statement_id=current_statement.id,
    limit=100
)
print(f"Found {len(transactions['items'])} transactions in current statement")

client.close()
```

### Advanced Usage

#### Concurrency with Async Client

```python
import asyncio
from iconic_api.client import IconicAsyncClient

async def fetch_data():
    client = IconicAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        instance_domain="your_instance.sellercenter.com.au"
    )
    
    # Execute multiple requests concurrently
    orders_task = client.orders.list_async(limit=10)
    products_task = client.product_sets.list_async(limit=10)
    brands_task = client.brands.list_async(limit=10)
    
    # Wait for all tasks to complete
    orders, products, brands = await asyncio.gather(
        orders_task, products_task, brands_task
    )
    
    print(f"Fetched {len(orders)} orders, {len(products)} products, and {len(brands)} brands")
    
    # Close the client when done
    await client.close()
    
    return orders, products, brands

# Run the async function
orders, products, brands = asyncio.run(fetch_data())
```

#### Working with Attributes

```python
from iconic_api.client import IconicClient
from iconic_api.resources.attribute_helper import AttributeHelper

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au"
)

# Get a category to work with
category = client.categories.get(123)  # Replace with actual category ID

# Get the attribute set for this category
attribute_set_id = category.attributeSetId
attribute_set = client.attribute_sets.get_attribute_set(attribute_set_id)

# Create an attribute helper
helper = AttributeHelper(attribute_set)

# Get an attribute by name
color_attribute = helper.get_attribute("Color")
if color_attribute:
    print(f"Color attribute ID: {color_attribute.id}")
    print(f"Input type: {color_attribute.input_type}")
    
    # If it's an option attribute, show available options
    if color_attribute.attribute_type == "option" and color_attribute.options:
        print("Available colors:")
        for option in color_attribute.options:
            print(f"  - {option.name} (ID: {option.id})")

# Prepare attributes for a product set
attributes = {
    "Color": "Red",  # Will be converted to the option ID
    "Size": "M",
    "Material": "Cotton",
    "Pattern": "Solid"
}

# Process attributes using the helper
prepared_attributes = helper.prepare_attributes(attributes)
print("Prepared attributes:", prepared_attributes)

client.close()
```

## Development

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/py-iconic-api.git
   cd py-iconic-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Documentation

For more details on the available endpoints and data models, please refer to the official [The Iconic SellerCenter API Documentation](https://sellercenter-api.theiconic.com.au/docs/).

## Additional Information

### Rate Limiting

The client respects rate limits imposed by The Iconic API. You can configure rate limiting behavior:

```python
from iconic_api.client import IconicClient

client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au",
    rate_limit_rps=20,  # Requests per second
    redis_url="redis://localhost:6379/0"  # Optional Redis for distributed rate limiting
)
```

### Error Handling

The client automatically handles retries for rate limit errors and transient failures. You can customize retry behavior:

```python
client = IconicClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    instance_domain="your_instance.sellercenter.com.au",
    max_retries=3,
    timeout=30.0  # Timeout in seconds
)
```

## License

This project is licensed under the CC BY-NC 4.0 License - see the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
