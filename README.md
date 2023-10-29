# Restocks.net API Wrapper

## Overview
The `restocks_api_wrapper` is an **unofficial** wrapper for the api of the sneaker platform restocks.net. It allows you to get information about products, but also to manage your sales. There is no connection to restocks, this is a private project.

## Functions

| Function Name         | Description                                         | Login Required |
|-----------------------|-----------------------------------------------------|----------------|
| `search_product`      | Searches for a product by SKU or name.              | No             |
| `get_product_info`    | Retrieves detailed information about a product.     | No             |
| `get_size_id`         | Fetches the size ID for a given product and size.   | No             |
| `get_sku_from_id`     | Retrieves the SKU for a product based on its ID.    | No             |
| `get_payout`          | Calculates the expected payout for a listing.       | No             |
| `login`               | Authenticates the user with email and password.     | No             |
| `check_login`         | Checks if the user is logged in.                    | Yes            |
| `get_current_listings`| Retrieves current product listings.                 | Yes            |
| `get_history_sales`   | Fetches historical sales data.                      | Yes            |
| `get_current_sales`   | Fetches current sales data.                         | Yes            |
| `edit_listing`        | Edits the price of an existing listing.             | Yes            |
| `delete_listing`      | Deletes an existing listing.                        | Yes            |
| `list_product`        | Lists a new product for sale.                       | Yes            |
| `get_shipping_products` | Retrieves products that need shipping.            | Yes            |
| `download_label`      | Downloads the shipping label for a product.         | Yes            |
| `check_consign_status`| Checks the consignment status of the user.          | Yes            |

## Usage Example

```python
from restocks_client import RestocksClient
from filters import SellMethod, ListingDuration

# Initialize the RestocksClient with login credentials and proxy list.
client = RestocksClient(
    email='your_email@example.com',
    password='your_password',
    proxy_list=[
        "proxy1:port:username:password",
        "proxy2:port:username:password",
        # ... (Add more proxies as needed)
    ]
)

# Authenticate and login.
client.login()

# Fetch information about a product using its SKU.
product_info = client.get_product_info(slug=client.search_product(sku='DD1391-100').slug)

# Retrieve current listings with a specific sell method.
current_listings = client.get_current_listings(sell_method=SellMethod.Resell)

# List a product for sale on the platform.
client.list_product(
    product=client.search_product(sku='DD1391-100'),
    size='36',
    sell_method=SellMethod.Resell,
    duration=ListingDuration.Days90,
    store_price=900
)

# Example of working with listings.
listing = current_listings[1]
client.delete_listing(listing.listing_id)
```

## Note
I recommend the use of proxies, which can be specified as a list as shown in the example. The format `hostname:port:username:password` is used for this. The use of proxies helps to avoid blocks of restocks. If no proxy list is given, the localhost is used by default.
