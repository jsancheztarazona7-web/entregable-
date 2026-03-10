from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from ..database import get_db
from ..models import Product, ProductPrice, Provider, Category

router = APIRouter(prefix="/products", tags=["Productos"])

class ProductCreate(BaseModel):
    code        : str
    name        : str
    description : Optional[str] = None
    unit        : str = "UND"
    category_id : Optional[int] = None
    brand       : Optional[str] = None

class PriceCreate(BaseModel):
    provider_id : int
    price       : float
    tax_percent : float = 19.0

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == 1).all()
    result = []
    for p in products:
        prices = db.query(ProductPrice).filter(
            ProductPrice.product_id == p.id,
            ProductPrice.is_active == 1
        ).all()
        price_list = []
        for pr in prices:
            provider = db.query(Provider).filter(Provider.id == pr.provider_id).first()
            price_list.append({
                "provider_id"   : pr.provider_id,
                "provider_name" : provider.name if provider else "",
                "price"         : float(pr.price),
                "tax_percent"   : float(pr.tax_percent),
                "price_with_tax": float(pr.price) * (1 + float(pr.tax_percent) / 100)
            })
        best_price = min(price_list, key=lambda x: x["price"]) if price_list else None
        result.append({
            "id"          : p.id,
            "code"        : p.code,
            "name"        : p.name,
            "description" : p.description,
            "unit"        : p.unit,
            "brand"       : p.brand,
            "category_id" : p.category_id,
            "prices"      : price_list,
            "best_price"  : best_price
        })
    return result

@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.code == product.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de producto ya existe")
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"message": "Producto creado", "id": db_product.id}

@router.put("/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    return {"message": "Producto actualizado"}

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db_product.is_active = 0
    db.commit()
    return {"message": "Producto eliminado"}

@router.post("/{product_id}/prices")
def add_price(product_id: int, price_data: PriceCreate, db: Session = Depends(get_db)):
    existing = db.query(ProductPrice).filter(
        ProductPrice.product_id == product_id,
        ProductPrice.provider_id == price_data.provider_id
    ).first()
    if existing:
        existing.price       = price_data.price
        existing.tax_percent = price_data.tax_percent
        existing.is_active   = 1
        db.commit()
        return {"message": "Precio actualizado"}
    db_price = ProductPrice(product_id=product_id, **price_data.model_dump())
    db.add(db_price)
    db.commit()
    return {"message": "Precio agregado"}