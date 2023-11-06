import random


def format_proxy(proxy_str):
    """
    Formats a single proxy string for the 'requests' library.

    Args:
        proxy_str (str): Proxy in the format "ip:port:user:password".

    Returns:
        dict: Formatted proxy suitable for the 'requests' library.
    """
    if proxy_str is None:
        return None
    # Check if the proxy is already formatted
    if "http://" in str(proxy_str) or "https://" in str(proxy_str):
        return proxy_str
    ip, port, user, password = proxy_str.split(':')
    return {
        'http': f'http://{user}:{password}@{ip}:{port}',
        'https': f'http://{user}:{password}@{ip}:{port}',
    }


def load_proxies_restocks(proxy_list):
    """
    Loads and formats the proxy list for Restocks API.

    Args:
        proxy_list (list or None): List of proxies in the format "ip:port:user:password". None if no proxies are provided.

    Returns:
        list or None: List of formatted proxies suitable for the 'requests' library. None if no proxies are provided.
    """
    if proxy_list is None:
        return None
    return [format_proxy(p) for p in proxy_list]


def get_random_proxy(proxy_list):
    """
    Returns a random proxy from the provided proxy list.

    Args:
        proxy_list (list or None): List of formatted proxies suitable for the 'requests' library. None if no proxies are provided.

    Returns:
        dict or None: A randomly selected proxy. None if no proxies are provided.
    """
    if proxy_list is None:
        return None
    return random.choice(proxy_list)
