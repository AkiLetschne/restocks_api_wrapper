from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional, Self

from .utils.helpers import parse_int, parse_size


class Variant(NamedTuple):
    """
    Represents a product variant, including its size, size ID, price, and availability status.
    """
    size: str
    size_id: int
    price: Optional[int]
    oos: bool

    @classmethod
    def _from_json(cls, data: dict):
        for entry in data:
            size = entry.get("size")
            price = entry.get("price")
            size_id = entry.get("size_id")
            yield Variant(size=size, price=price, oos=not price, size_id=size_id)


class Shipping(NamedTuple):
    """
    Represents shipping details, including label URL and shipping deadline.
    """
    label_url: str
    ship_before: datetime

    @classmethod
    def _from_json(cls, data: dict):
        ship_before = datetime.strptime(data['ship_before'], "%d/%m/%y")
        return Shipping(label_url=data['label_url'], ship_before=ship_before)


@dataclass
class Product:
    """
    Represents a product, including its name, SKU, image URL, and other relevant details.
    """
    name: str
    sku: str
    slug: str
    image: str
    id: int
    price: int

    listing_id: Optional[int]
    size: Optional[str]
    variants: Optional[list[Variant]]
    date: Optional[datetime]
    shipping: Optional[Shipping]

    @classmethod
    def _from_json(cls, data: dict) -> Self:
        from restocks_client.utils.helpers import get_sku
        return Product(
            name=data["name"],
            image=data["image"].replace("width=80", "width=500"),
            slug=data["slug"],
            sku=get_sku(image=data['image'], baseproduct_id=data['id']) if not data.get('sku') else data['sku'],
            id=parse_int(data["id"]),
            price=parse_int(data["price"]) if data.get("price") else None,
            listing_id=parse_int(data["listing_id"]) if data.get("listing_id") else None,
            size=parse_size(data["size"]) if data.get("size") else None,
            variants=[v for v in Variant._from_json(data["variants"])] if data.get("variants") else None,
            date=datetime.strptime(data["date"], "%d/%m/%y") if data.get("date") else None,
            shipping=Shipping._from_json(data['shipping']) if data.get('shipping') else None
        )
