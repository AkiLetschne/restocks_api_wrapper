import requests
from requests import Response

from .exceptions import SessionException, LoginException, RequestException
from .product import Product
from .filters import SellMethod, ListingDuration
from .utils.helpers import get_sku, parse_size, parse_int
from .utils.defaults import BASE_URL, DEFAULT_HEADERS
from .utils.proxy_handler import get_random_proxy, load_proxies_restocks


class RestocksClient:
    """
    A client for interacting with the Restocks API. This client allows users to authenticate, make requests, and manage their interactions
    with the Restocks platform.

    Attributes:
        email (str, optional): Email used for authentication. Defaults to None.
        password (str, optional): Password associated with the given email for authentication. Defaults to None.
        session (requests.Session): Active session used for API requests.
        headers (dict): Headers used for API requests, including the default ones.
        proxy_list (list or None): List of proxies in the format [`ip:port:user:password`] to rotate through for the requests. Defaults to None if proxies aren't provided.
    """

    def __init__(self, email=None, password=None, proxy_list=None):
        """
        Creates a new instance of the RestocksClient, initializing necessary attributes.

        Args:
            email (str, optional): Email used for authentication. Defaults to None.
            password (str, optional): Password for authentication. Defaults to None.
            proxy_list (list or None): List of proxies in the format [`ip:port:user:password`] to be used during requests. If not provided, defaults to None.
        """
        self.email = email
        self.password = password
        self.session = requests.session()
        self.headers = DEFAULT_HEADERS
        self.proxy_list = load_proxies_restocks(proxy_list)

    # login required methods
    def _get_country_of_user(self) -> str:
        shipping_address_response = self.session.get(f'{BASE_URL}/shop/account/shipping-address', headers=self.headers,
                                                     proxies=get_random_proxy(self.proxy_list))
        self._validate_response(shipping_address_response, 200)

        data = shipping_address_response.json()
        return data['data']['country']

    def _set_country_headers(self):
        country_response = self.session.get(f'{BASE_URL}/countries', headers=self.headers)
        self._validate_response(country_response, 200)

        country_code = self._get_country_of_user()
        self.headers['restocks-country'] = country_code
        data = country_response.json()
        for item in data['data']:
            if item['code'] == country_code:
                self.headers['accept-language'] = item['default']['language']
                self.headers['restocks-valuta'] = item['default']['valuta']

    def check_login(self) -> bool:
        """
        Checks if the user is logged in.

        Returns:
            bool: True if logged in, False otherwise.
        """
        check_login_request = self.session.get(f'{BASE_URL}/shop/account/profile',
                                               proxies=get_random_proxy(self.proxy_list),
                                               headers=self.headers)
        if check_login_request.status_code == 200:
            return True
        else:
            return False

    def login(self, email=None, password=None) -> bool:
        """
        Authenticates the user using the provided email and password. If credentials are not provided,
        it uses the credentials stored in the class instance.

        Args:
            email (str, optional): Email used for authentication. If provided, it updates the class email attribute.
            password (str, optional): Password for authentication. If provided, it updates the class password attribute.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        if email is not None:
            self.email = email
        if password is not None:
            self.password = password

        if self.email is None or self.password is None:
            raise LoginException('Email and password must be provided for authentication.')

        json_data = {
            'email': self.email,
            'password': self.password,
        }

        login_response = self.session.post(f'{BASE_URL}/auth/login', headers=self.headers,
                                           json=json_data, proxies=get_random_proxy(self.proxy_list))
        if login_response.status_code == 200:
            self.headers['Authorization'] = f"Bearer {login_response.json()['data']['token']}"
            self._set_country_headers()
            return True
        else:
            raise LoginException(f'Login failed with status code: {login_response.status_code}')

    def get_current_listings(self, sell_method: str) -> list[Product]:
        """
        Retrieves a list of current product listings based on the provided selling method.

        Args:
            sell_method (str): The method used for selling (e.g. 'direct', 'consign').

        Returns:
            list[Product]: A list of Product objects representing the current listings.
        """
        data = self._current_listings_request(page=1, sell_method=sell_method)
        total_pages = data["meta"]["last_page"]

        all_data = []
        all_data.extend(data["data"])

        for page in range(2, total_pages + 1):
            data = self._current_listings_request(page=page, sell_method=sell_method)
            all_data.extend(data["data"])

        listings = []
        for p in all_data:
            product = {
                'name': p['baseproduct']['name'],
                'image': p['baseproduct']['image_url'],
                'sku': get_sku(image=p['baseproduct']['image_url'], baseproduct_id=p['id']),
                'slug': p['baseproduct']['slug'],
                'id': p['baseproduct']['id'],
                'size': p['size']['name'],
                'price': p['price']['valuta_price'],
                'listing_id': p['id']
            }
            listings.append(Product._from_json(product))

        return listings

    def _current_listings_request(self, page, sell_method) -> dict:
        listing_resp = self.session.get(f'{BASE_URL}/shop/account/listings/{sell_method}?page={page}',
                                        headers=self.headers, proxies=get_random_proxy(self.proxy_list))
        self._validate_response(listing_resp, 200)
        return listing_resp.json()

    def get_history_sales(self) -> list[Product]:
        """
        Retrieves a list of historical sales for the authenticated user.

        Returns:
            list[Product]: A list of Product objects representing the historical sales.
        """

        data = self._history_sales_request(page=1)
        total_pages = data["meta"]["last_page"]

        all_data = []
        all_data.extend(data["data"])

        for page in range(2, total_pages + 1):
            data = self._history_sales_request(page=page)
            all_data.extend(data["data"])

        sales = []
        for p in all_data:
            product = {
                'name': p['baseproduct']['name'],
                'image': p['baseproduct']['image_url'],
                'sku': get_sku(image=p['baseproduct']['image_url'], baseproduct_id=p['id']),
                'slug': None,
                'id': p['baseproduct']['id'],
                'size': p['size']['name'],
                'price': p['payout'],
                'listing_id': p['id'],
                'date': p['date']
            }
            sales.append(Product._from_json(product))

        return sales

    def _history_sales_request(self, page) -> dict:
        sale_resp = self.session.get(f'{BASE_URL}/shop/account/sales/history?page={page}',
                                     headers=self.headers, proxies=get_random_proxy(self.proxy_list))
        self._validate_response(sale_resp, 200)
        return sale_resp.json()

    def get_current_sales(self) -> list[Product]:
        """
        Retrieves a list of current sales for the authenticated user.

        Returns:
            list[Product]: A list of Product objects representing the current sales.
        """
        # TODO: check if response is the same, there is prob a status or something

        data = self._current_sales_request(page=1)
        total_pages = data["meta"]["last_page"]

        all_data = []
        all_data.extend(data["data"])

        for page in range(2, total_pages + 1):
            data = self._current_sales_request(page=page)
            all_data.extend(data["data"])

        sales = []
        for p in all_data:
            product = {
                'name': p['baseproduct']['name'],
                'image': p['baseproduct']['image_url'],
                'sku': get_sku(image=p['baseproduct']['image_url'], baseproduct_id=p['id']),
                'slug': None,
                'id': p['baseproduct']['id'],
                'size': p['size']['name'],
                'price': p['payout'],
                'listing_id': p['id'],
                'date': p['date']
            }
            sales.append(Product._from_json(product))

        return sales

    def _current_sales_request(self, page) -> dict:
        sale_resp = self.session.get(f'{BASE_URL}/shop/account/sales/sold?page={page}',
                                     headers=self.headers, proxies=get_random_proxy(self.proxy_list))
        self._validate_response(sale_resp, 200)
        return sale_resp.json()

    def edit_listing(self, listing_id: int, new_price: int) -> bool:
        """
        Edits the price of an existing listing.

        Args:
            listing_id (int): The ID of the listing to be edited.
            new_price (int): The new price for the listing.

        Returns:
            bool: True if the edit was successful, False otherwise.
        """
        json_data = {
            'price': new_price,
        }

        edit_response = self.session.put(f'{BASE_URL}/shop/account/listings/{listing_id}', json=json_data,
                                         proxies=get_random_proxy(self.proxy_list), headers=self.headers)
        self._validate_response(edit_response, 200)
        return True

    def delete_listing(self, listing_id: int) -> bool:
        """
        Deletes an existing listing.

        Args:
            listing_id (int): The ID of the listing to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        delete_response = self.session.delete(f'{BASE_URL}/shop/account/listings/{listing_id}',
                                              proxies=get_random_proxy(self.proxy_list), headers=self.headers)
        resp = self._validate_response(delete_response, 200).json()['data']
        return resp.get('success', False)

    def _get_payout(self, store_price: int, sell_method: SellMethod, currency: str = 'EUR') -> float:
        payout_response = self.session.get(
            f'{BASE_URL}/shop/listings/pricing?price={store_price}&sell_method={sell_method}&currency={currency}',
            proxies=get_random_proxy(self.proxy_list), headers=self.headers)
        resp = self._validate_response(payout_response, 200).json()['data']
        return float(resp['payout']['amount'])

    def list_product(self, product: Product, size: str, store_price: int, sell_method: SellMethod,
                     duration: ListingDuration) -> bool:
        """
        Lists a product for sale on the platform.

        Args:
            product (Product): The product to be listed.
            size (str): The size of the product.
            store_price (int): The price at which the product is listed.
            sell_method (SellMethod): The method used for selling (e.g. 'direct', 'consign').
            duration (ListingDuration): The duration for which the listing will be active.

        Returns:
            bool: True if the product was listed successfully, False otherwise.
        """
        size_id = self.get_size_id(baseproduct_id=product.id, size=size)
        if not size_id:
            raise SessionException("invalid size")

        json_data = {
            'listings': [
                {
                    'baseproduct_id': product.id,
                    'size_id': size_id,
                    'condition': True,
                    'amount': 1,
                    'store_price': store_price,
                    'sell_method': sell_method,
                    'duration': duration,
                },
            ],
        }

        create_listing_response = self.session.post(f'{BASE_URL}/shop/account/sell',
                                                    proxies=get_random_proxy(self.proxy_list),
                                                    headers=self.headers, json=json_data)
        resp = self._validate_response(create_listing_response, 200).json()['data']
        return resp.get('success', False)

    def get_shipping_products(self) -> [Product]:
        """
        Retrieves a list of products that need to be shipped.

        Returns:
            list[Product]: A list of Product objects that need to be shipped.
        """
        # get all current sales
        data = self._current_sales_request(page=1)
        total_pages = data["meta"]["last_page"]

        current_sales_data = []
        current_sales_data.extend(data["data"])

        for page in range(2, total_pages + 1):
            data = self._current_sales_request(page=page)
            current_sales_data.extend(data["data"])

        # get all current consign listings
        data = self._current_listings_request(page=1, sell_method=SellMethod.Consign)
        total_pages = data["meta"]["last_page"]

        current_consign_listings_data = []
        current_consign_listings_data.extend(data["data"])

        for page in range(2, total_pages + 1):
            data = self._current_listings_request(page=page, sell_method=SellMethod.Consign)
            current_consign_listings_data.extend(data["data"])

        all_data = []
        all_data.extend(current_sales_data)
        all_data.extend(current_consign_listings_data)

        shipping_products = []
        for p in all_data:
            if not p.get('ship_before'):
                continue

            product = {
                'name': p['baseproduct']['name'],
                'image': p['baseproduct']['image_url'],
                'sku': get_sku(image=p['baseproduct']['image_url'], baseproduct_id=p['id']),
                'slug': p['baseproduct']['slug'],
                'id': p['baseproduct']['id'],
                'size': p['size']['name'],
                'price': p['price']['text'],
                'listing_id': p['id'],
                'shipping': {
                    'label_url': p['action']['link'],
                    'ship_before': p['ship_before']
                }
            }
            shipping_products.append(Product._from_json(product))
        return shipping_products

    def download_label(self, product: Product, path: str) -> str:
        """
        Downloads the shipping label for a given product.

        Args:
            product (Product): The product for which the label is to be downloaded.
            path (str): The path where the label should be saved.

        Returns:
            str: The format of the label (e.g. 'GIF', 'PDF').
        """
        get_label_request = self.session.get(product.shipping.label_url, proxies=get_random_proxy(self.proxy_list),
                                             headers=self.headers, allow_redirects=True, stream=True)
        self._validate_response(get_label_request, 200)
        file_format = get_label_request.text[0:4]
        if file_format == "GIF8":
            open(f'{path}{product.listing_id}.gif', 'wb').write(get_label_request.content)
            return 'GIF'
        elif file_format == "%PDF":
            with open(f'{path}{product.listing_id}.pdf', 'wb') as f:
                f.write(get_label_request.content)
                f.close()
            return 'PDF'

    def check_consign_status(self) -> bool:
        """
        Checks the consignment status for the authenticated user.

        Returns:
            bool: True if consignment is unlocked, False otherwise.
        """
        config_response = self.session.get(f'{BASE_URL}/shop/account/sell/config',
                                           proxies=get_random_proxy(self.proxy_list),
                                           headers=self.headers)
        resp = self._validate_response(config_response, 200).json()['data']
        return True if not resp.get('is_consign_locked', False) else False

    # no login required methods
    def search_product(self, sku=None, name=None) -> Product or None:
        """
        Search for a product either by its SKU or name.

        Args:
            sku (str, optional): The SKU of the product to search for.
            name (str, optional): The name of the product to search for.
            headers (dict, optional): Custom headers for the request.
            proxy (dict, optional): Proxy configuration for the request.

        Returns:
            Product: A product object if found, None otherwise.
        """
        if not (bool(sku) ^ bool(name)):  # if args are not correct
            raise ValueError("Either sku or name must be provided, but not both")

        query = sku or name
        params = {
            'query': query,
            'minimum_price': '0',
        }

        search_response = requests.get(f'{BASE_URL}/shop/catalog/autocomplete',
                                       proxies=get_random_proxy(self.proxy_list), params=params, headers=self.headers)

        if search_response.status_code != 200:
            return None

        data = search_response.json()['data']['products']
        if not data:
            return None

        product = data[0]
        product = {
            'name': product['name'],
            'image': product['image_url'],
            'sku': product['sku'],
            'slug': product['slug'],
            'id': product['id'],
        }
        return Product._from_json(product)

    def get_product_info(self, slug) -> Product:
        """
        Retrieves detailed information about a product based on its slug.

        Args:
            slug (str): The slug of the product.
            headers (dict, optional): Custom headers for the request.
            proxy (dict, optional): Proxy configuration for the request.

        Returns:
            Product: A product object containing detailed information.
        """
        session = requests.Session()

        product_info_url = f'{BASE_URL}/shop/baseproducts?slug={slug}'

        with session.get(product_info_url, headers=self.headers, proxies=get_random_proxy(self.proxy_list)) as \
                product_info_response:
            data = product_info_response.json()['data']

        name = data['name']
        baseproduct_id = data['id']
        image_url = data['image_urls'][0]
        sku = data['details'][0]['value']
        variants_raw = data['sizes']
        variants = []

        for entry in variants_raw:
            size = parse_size(entry['name'])
            size_id = entry['id']
            price = int(parse_int(entry['prices'][0]['store_price']['formatted_amount'])) if entry['prices'] else None
            variants.append({
                'size': size,
                'size_id': size_id,
                'price': price
            })

        product = {
            'name': name,
            'image': image_url,
            'sku': sku,
            'slug': slug,
            'id': baseproduct_id,
            'variants': variants
        }
        return Product._from_json(product)

    def get_size_id(self, baseproduct_id, size) -> str:
        """
        Retrieves the size ID for a given product and size.

        Args:
            baseproduct_id (int): The ID of the product.
            size (str): The size of the product.
            headers (dict, optional): Custom headers for the request.
            proxy (dict, optional): Proxy configuration for the request.

        Returns:
            int: The size ID if found, None otherwise.
        """
        url = f'{BASE_URL}/shop/baseproducts/{baseproduct_id}/sizes'

        with requests.get(url, proxies=get_random_proxy(self.proxy_list), headers=self.headers) as size_id_request:
            data = size_id_request.json()['data']

        size_id = None  # default value - size not found

        if '.5' in size:
            size = size.replace('.5', ' \u00bd')
        elif '1/3' in size:
            size = size.replace('1/3', '\u2153')
        elif '2/3' in size:
            size = size.replace('2/3', '\u2154')

        for sid in data:
            if str(sid['name']) == str(size):
                size_id = sid['id']
                break

        return size_id

    def get_sku_from_id(self, baseproduct_id) -> str:
        """
        Retrieves the SKU for a product based on its ID.

        Args:
            baseproduct_id (int): The ID of the product.
            headers (dict, optional): Custom headers for the request.
            proxy (dict, optional): Proxy configuration for the request.

        Returns:
            str: The SKU of the product.
        """
        response = requests.get(f'{BASE_URL}/shop/catalog/products?ids={baseproduct_id}',
                                proxies=get_random_proxy(self.proxy_list), headers=self.headers)
        return response.json()['data'][0]['sku']

    def get_payout(self, store_price: int, sell_method: SellMethod, currency: str = 'EUR') -> float:
        """
        Fetches the expected payout amount for a given product price, selling method, and currency.

        This method communicates with the Restocks API to determine the payout
        a user can expect when they list a product for sale at a given price,
        using a specified selling method, and in a particular currency.

        Args:
            store_price (int): The price at which the product is listed for sale.
            sell_method (SellMethod): The method used for selling (e.g. 'direct', 'consign').
            currency (str, optional): The currency in which the product is listed. Default is 'EUR'.

        Returns:
            float: The expected payout amount.
        """
        payout_response = requests.get(
            f'{BASE_URL}/shop/listings/pricing?price={store_price}&sell_method={sell_method}&currency={currency}',
            proxies=get_random_proxy(self.proxy_list), headers=self.headers)
        resp = self._validate_response(payout_response, 200).json()['data']
        return float(resp['payout']['amount'])

    # helper methods
    def _validate_response(self, response: Response, status_code: int, msg: str = None) -> Response:
        if response.status_code == status_code:
            return response

        if response.status_code in [404, 401] and not self.check_login():
            raise LoginException('It seems you are not logged in. Please log in and retry.')

        error_message = f'Request failed with status code {response.status_code}'
        if msg:
            error_message += f': {msg}'

        raise RequestException(error_message)
