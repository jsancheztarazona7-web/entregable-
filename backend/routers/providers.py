from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Provider

router = APIRouter(prefix="/providers", tags=["Proveedores"])

class ProviderCreate(BaseModel):
    code          : str
    name          : str
    contact_name  : Optional[str] = None
    email         : Optional[str] = None
    phone         : Optional[str] = None
    address       : Optional[str] = None
    nit           : Optional[str] = None
    payment_terms : int = 30
    delivery_days : int = 1

@router.get("/")
def get_providers(db: Session = Depends(get_db)):
    return db.query(Provider).filter(Provider.is_active == 1).all()

@router.post("/")
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    existing = db.query(Provider).filter(Provider.code == provider.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Código de proveedor ya existe")
    db_provider = Provider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return {"message": "Proveedor creado", "id": db_provider.id}

@router.put("/{provider_id}")
def update_provider(provider_id: int, provider: ProviderCreate, db: Session = Depends(get_db)):
    db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for key, value in provider.model_dump().items():
        setattr(db_provider, key, value)
    db.commit()
    return {"message": "Proveedor actualizado"}

@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db_provider.is_active = 0
    db.commit()
    return {"message": "Proveedor eliminado"}