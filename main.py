from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
#Adding imports
from models.product import ProductCreate, ProductRead, ProductUpdate
from models.order import OrderCreate, OrderRead, OrderUpdate, LineItem


port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
persons: Dict[UUID, PersonRead] = {}
addresses: Dict[UUID, AddressRead] = {}
#Adding in-memory stores
products: Dict[UUID, ProductRead] = {}
orders: Dict[UUID, OrderRead] = {}


app = FastAPI(
    title="Person/Address API",
    description="Demo FastAPI app using Pydantic v2 models for Person and Address",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Address endpoints
# -----------------------------------------------------------------------------

# Adding helper to compute order totals.
def compute_order_total(line_items: List[LineItem]) -> float:
    total = 0.0
    for li in line_items:
        prod = products.get(li.product_id)
        if not prod:
            raise HTTPException(status_code=400, detail=f"Unknown product_id: {li.product_id}")
        total += float(prod.price) * int(li.quantity)
    return round(total, 2)

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate):
    if address.id in addresses:
        raise HTTPException(status_code=400, detail="Address with this ID already exists")
    addresses[address.id] = AddressRead(**address.model_dump())
    return addresses[address.id]

@app.get("/addresses", response_model=List[AddressRead])
def list_addresses(
    street: Optional[str] = Query(None, description="Filter by street"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state/region"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    results = list(addresses.values())

    if street is not None:
        results = [a for a in results if a.street == street]
    if city is not None:
        results = [a for a in results if a.city == city]
    if state is not None:
        results = [a for a in results if a.state == state]
    if postal_code is not None:
        results = [a for a in results if a.postal_code == postal_code]
    if country is not None:
        results = [a for a in results if a.country == country]

    return results

@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: UUID):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return addresses[address_id]

@app.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, update: AddressUpdate):
    if address_id not in addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    stored = addresses[address_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    addresses[address_id] = AddressRead(**stored)
    return addresses[address_id]

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------
@app.post("/persons", response_model=PersonRead, status_code=201)
def create_person(person: PersonCreate):
    # Each person gets its own UUID; stored as PersonRead
    person_read = PersonRead(**person.model_dump())
    persons[person_read.id] = person_read
    return person_read

@app.get("/persons", response_model=List[PersonRead])
def list_persons(
    uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    city: Optional[str] = Query(None, description="Filter by city of at least one address"),
    country: Optional[str] = Query(None, description="Filter by country of at least one address"),
):
    results = list(persons.values())

    if uni is not None:
        results = [p for p in results if p.uni == uni]
    if first_name is not None:
        results = [p for p in results if p.first_name == first_name]
    if last_name is not None:
        results = [p for p in results if p.last_name == last_name]
    if email is not None:
        results = [p for p in results if p.email == email]
    if phone is not None:
        results = [p for p in results if p.phone == phone]
    if birth_date is not None:
        results = [p for p in results if str(p.birth_date) == birth_date]

    # nested address filtering
    if city is not None:
        results = [p for p in results if any(addr.city == city for addr in p.addresses)]
    if country is not None:
        results = [p for p in results if any(addr.country == country for addr in p.addresses)]

    return results

@app.get("/persons/{person_id}", response_model=PersonRead)
def get_person(person_id: UUID):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons[person_id]

@app.patch("/persons/{person_id}", response_model=PersonRead)
def update_person(person_id: UUID, update: PersonUpdate):
    if person_id not in persons:
        raise HTTPException(status_code=404, detail="Person not found")
    stored = persons[person_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    persons[person_id] = PersonRead(**stored)
    return persons[person_id]



# -----------------------------------------------------------------------------
# Product endpoints
# -----------------------------------------------------------------------------
@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate):
    if product.id in products:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    prod = ProductRead(**product.model_dump())
    products[prod.id] = prod
    return prod

@app.get("/products", response_model=List[ProductRead])
def list_products(
    name: Optional[str] = Query(None, description="Filter by case-insensitive name substring"),
):
    results = list(products.values())
    if name:
        name_l = name.lower()
        results = [p for p in results if name_l in p.name.lower()]
    return results

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID = Path(..., description="Product ID")):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]

@app.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: UUID, patch: ProductUpdate):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    data = products[product_id].model_dump()
    updates = patch.model_dump(exclude_unset=True)
    data.update(updates)
    # Update timestamp on modification
    data["updated_at"] = datetime.utcnow()
    updated = ProductRead(**data)
    products[product_id] = updated
    return updated

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: UUID):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    del products[product_id]
    return None


# -----------------------------------------------------------------------------
# Order endpoints
# -----------------------------------------------------------------------------
@app.post("/orders", response_model=OrderRead, status_code=201)
def create_order(order: OrderCreate):
    # Compute total (validates product IDs)
    total = compute_order_total(order.items)
    data = order.model_dump()
    data["total_amount"] = total
    orr = OrderRead(**data)
    if orr.id in orders:
        raise HTTPException(status_code=400, detail="Order with this ID already exists")
    orders[orr.id] = orr
    return orr

@app.get("/orders", response_model=List[OrderRead])
def list_orders(
    customer_name: Optional[str] = Query(None, description="Filter by case-insensitive customer name substring"),
):
    results = list(orders.values())
    if customer_name:
        key = customer_name.lower()
        results = [o for o in results if key in o.customer_name.lower()]
    return results

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID = Path(..., description="Order ID")):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.patch("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: UUID, patch: OrderUpdate):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    data = orders[order_id].model_dump()
    updates = patch.model_dump(exclude_unset=True)

    if "customer_name" in updates and updates["customer_name"] is not None:
        data["customer_name"] = updates["customer_name"]

    if "items" in updates and updates["items"] is not None:
        data["items"] = updates["items"]
        data["total_amount"] = compute_order_total(updates["items"])

    if "note" in updates:
        data["note"] = updates["note"]

    # Update timestamp on modification
    data["updated_at"] = datetime.utcnow()

    updated = OrderRead(**data)
    orders[order_id] = updated
    return updated

@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: UUID):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    del orders[order_id]
    return None

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
