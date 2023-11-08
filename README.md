# Restocks.net API Wrapper

## Overview
The `restocks_api_wrapper` is an **unofficial** wrapper for the api of the sneaker platform restocks.net. It allows you to get information about products, but also to manage your sales. There is no connection to restocks, this is a private project.

## Installation

Install the package using pip:

```bash
pip install restocks-api-wrapper
```
Ensure that you are using Python 3.11 or higher, as this is the minimum version required for this package.

## Functions
The following table describes each function available in the RestocksClient object, along with whether a user login is required to use the function.

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

### Filters

When listing a product or retrieving current listings, you can specify filters to narrow down the results or to set the conditions of your listing. Below are the filter types and their possible values:

#### ListingDuration
This filter is used to specify the duration for which a product will be listed on the platform. The possible values are:

- `Days30`: List the product for 30 days.
- `Days60`: List the product for 60 days.
- `Days90`: List the product for 90 days.

#### SellMethod
This filter is used to define the method of sale. The possible values are:

- `Consign`: The product is sold on consignment.
- `Resell`: The product is resold directly.

Refer to the usage example below to see how these filters are applied in method calls.

## Usage Example

```python
from restocks_client.client import RestocksClient
from restocks_client.filters import SellMethod, ListingDuration

# Initialize the RestocksClient with login credentials and proxy list.
client = RestocksClient(
    proxy_list=[
        "proxy1:port:username:password",
        "proxy2:port:username:password",
        # ... (Add more proxies as needed)
    ]
)

# Fetch information about a product using its SKU.
product_info = client.get_product_info(slug=client.search_product(sku='DD1391-100').slug)

# login data
email = 'your_email@example.com',
password = 'your_password',

# Authenticate and login.
client.login(email, password)

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
client.edit_listing(listing_id=listing.listing_id, new_price=500)

for listing in current_listings:
    client.delete_listing(listing.listing_id)
```

## Note
I recommend the use of proxies, which can be specified as a list as shown in the example. The format `hostname:port:username:password` is used for this. The use of proxies helps to avoid blocks of restocks. If no proxy list is given, the localhost is used by default.

## Credits

This project was inspired by the structure of [ssbanjo's Restocks-client](https://github.com/ssbanjo/Restocks-client). While `restocks_api_wrapper` is a completely independent and updated implementation, the design and workflow provided a starting point for development. Many thanks to the original author for their work.

