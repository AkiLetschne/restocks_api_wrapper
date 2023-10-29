import re


def parse_int(number_str: str) -> int:
    return int(re.search(r'\d+', str(number_str).replace(".", "")).group(0))


def parse_size(size_str: str) -> str:
    num = re.search(r'\d+', size_str).group(0)

    if ".5" in size_str or "½" in size_str:
        return num + ".5"
    elif "⅔" in size_str:
        return num + " 2/3"
    elif "⅓" in size_str:
        return num + " 1/3"
    else:
        return num


def get_sku(image: str, baseproduct_id) -> str:
    try:
        return _image_to_sku(image)
    except IndexError:
        from ..restocks_api import get_sku_from_id
        return get_sku_from_id(baseproduct_id)


def _image_to_sku(image: str) -> str:
    return re.findall('/products/(.*?)/', image)[0]
