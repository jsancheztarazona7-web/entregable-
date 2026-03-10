from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..database import get_db
from ..models import Quote, QuoteItem, Product, Provider

router = APIRouter(prefix="/quotes", tags=["Cotizaciones"])

class QuoteItemCreate(BaseModel):
    product_id  : int
    provider_id : int
    quantity    : float
    unit_price  : float
    tax_percent : float = 19.0

class QuoteCreate(BaseModel):
    client_name  : str
    client_email : Optional[str] = None
    client_phone : Optional[str] = None
    notes        : Optional[str] = None
    items        : List[QuoteItemCreate]

@router.get("/")
def get_quotes(db: Session = Depends(get_db)):
    quotes = db.query(Quote).order_by(Quote.created_at.desc()).all()
    return [{"id": q.id, "quote_number": q.quote_number,
             "client_name": q.client_name, "total_amount": float(q.total_amount),
             "status": q.status, "created_at": q.created_at} for q in quotes]

@router.get("/{quote_id}")
def get_quote_detail(quote_id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
    item_list = []
    for item in items:
        product  = db.query(Product).filter(Product.id == item.product_id).first()
        provider = db.query(Provider).filter(Provider.id == item.provider_id).first()
        item_list.append({
            "product_name"  : product.name if product else "",
            "product_code"  : product.code if product else "",
            "unit"          : product.unit if product else "",
            "provider_name" : provider.name if provider else "",
            "quantity"      : float(item.quantity),
            "unit_price"    : float(item.unit_price),
            "tax_percent"   : float(item.tax_percent),
            "subtotal"      : float(item.subtotal)
        })
    return {
        "id"           : quote.id,
        "quote_number" : quote.quote_number,
        "client_name"  : quote.client_name,
        "client_email" : quote.client_email,
        "client_phone" : quote.client_phone,
        "notes"        : quote.notes,
        "total_amount" : float(quote.total_amount),
        "status"       : quote.status,
        "created_at"   : quote.created_at,
        "items"        : item_list
    }

@router.post("/")
def create_quote(quote: QuoteCreate, db: Session = Depends(get_db)):
    number     = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total      = sum(i.quantity * i.unit_price * (1 + i.tax_percent / 100) for i in quote.items)
    db_quote   = Quote(
        quote_number = number,
        client_name  = quote.client_name,
        client_email = quote.client_email,
        client_phone = quote.client_phone,
        notes        = quote.notes,
        total_amount = total
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    for item in quote.items:
        subtotal = item.quantity * item.unit_price * (1 + item.tax_percent / 100)
        db_item  = QuoteItem(
            quote_id    = db_quote.id,
            product_id  = item.product_id,
            provider_id = item.provider_id,
            quantity    = item.quantity,
            unit_price  = item.unit_price,
            tax_percent = item.tax_percent,
            subtotal    = subtotal
        )
        db.add(db_item)
    db.commit()
    return {"message": "Cotización creada", "quote_number": number, "total": total}

@router.put("/{quote_id}/status")
def update_status(quote_id: int, status: str, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    quote.status = status
    db.commit()
    return {"message": "Estado actualizado"}