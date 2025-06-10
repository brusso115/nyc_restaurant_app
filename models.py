from dataclasses import dataclass
from typing import Optional
from datetime import time, datetime
import html

@dataclass
class Restaurant:
    name: str
    url: str
    categories: str
    address: str
    city: str
    region: str
    postal_code: str
    country: str
    latitude: float
    longitude: float
    telephone: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]


    @classmethod
    def from_json(cls, data: dict, link: str) -> "Restaurant":
        return cls(
            name=html.unescape(data["name"]),
            url=link,
            categories=html.unescape(", ".join(data.get("servesCuisine", []))),
            address=data["address"]["streetAddress"],
            city=data["address"]["addressLocality"],
            region=data["address"]["addressRegion"],
            postal_code=data["address"]["postalCode"],
            country=data["address"]["addressCountry"],
            latitude=data["geo"]["latitude"],
            longitude=data["geo"]["longitude"],
            telephone=data.get("telephone"),
            rating=data.get("aggregateRating", {}).get("ratingValue"),
            review_count=data.get("aggregateRating", {}).get("reviewCount"),
        )

@dataclass
class MenuItem:
    restaurant_id: int
    section: str
    name: str
    description: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    embedded: bool = False

    @classmethod
    def from_json(cls, restaurant_id: int, section_name: str, item: dict) -> "MenuItem":
        return cls(
            restaurant_id=restaurant_id,
            section=html.unescape(section_name),
            name=html.unescape(item.get("name", "")),
            description=html.unescape(item.get("description", "")),
            price=item.get("offers", {}).get("price"),
            currency=item.get("offers", {}).get("priceCurrency"),
            embedded=False
        )

@dataclass
class RestaurantHours:
    restaurant_id: int
    day: str
    opens: time
    closes: time

    @classmethod
    def from_json(cls, restaurant_id: int, day: str, entry: dict) -> "RestaurantHours":
        return cls(
            restaurant_id=restaurant_id,
            day=day,
            opens=datetime.strptime(entry["opens"], "%H:%M").time(),
            closes=datetime.strptime(entry["closes"], "%H:%M").time()
        )