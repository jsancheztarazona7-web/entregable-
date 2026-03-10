from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(String(500))
    is_active   = Column(Integer, default=1)
    created_at  = Column(DateTime, default=datetime.now)
    products    = relationship("Product", back_populates="category")

class Provider(Base):
    __tablename__ = "providers"
    id            = Column(Integer, primary_key=True, index=True)
    code          = Column(String(20), unique=True, nullable=False)
    name          = Column(String(200), nullable=False)
    contact_name  = Column(String(200))
    email         = Column(String(200))
    phone         = Column(String(50))
    address       = Column(String(500))
    nit           = Column(String(50))
    payment_terms = Column(Integer, default=30)
    delivery_days = Column(Integer, default=1)
    is_active     = Column(Integer, default=1)
    created_at    = Column(DateTime, default=datetime.now)
    prices        = relationship("ProductPrice", back_populates="provider")

class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, index=True)
    code        = Column(String(50), unique=True, nullable=False)
    name        = Column(String(200), nullable=False)
    description = Column(String(1000))
    unit        = Column(String(30), default="UND")
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand       = Column(String(100))
    is_active   = Column(Integer, default=1)
    created_at  = Column(DateTime, default=datetime.now)
    category    = relationship("Category", back_populates="products")
    prices      = relationship("ProductPrice", back_populates="product")

class ProductPrice(Base):
    __tablename__ = "product_prices"
    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    price       = Column(Numeric(18, 2), nullable=False)
    tax_percent = Column(Numeric(5, 2), default=19.0)
    is_active   = Column(Integer, default=1)
    updated_at  = Column(DateTime, default=datetime.now)
    product     = relationship("Product", back_populates="prices")
    provider    = relationship("Provider", back_populates="prices")

class Quote(Base):
    __tablename__ = "quotes"
    id           = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(20), unique=True, nullable=False)
    client_name  = Column(String(200), nullable=False)
    client_email = Column(String(200))
    client_phone = Column(String(50))
    notes        = Column(String(1000))
    total_amount = Column(Numeric(18, 2), default=0)
    status       = Column(String(20), default="BORRADOR")
    created_at   = Column(DateTime, default=datetime.now)
    items        = relationship("QuoteItem", back_populates="quote")

class QuoteItem(Base):
    __tablename__ = "quote_items"
    id          = Column(Integer, primary_key=True, index=True)
    quote_id    = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    quantity    = Column(Numeric(18, 2), nullable=False)
    unit_price  = Column(Numeric(18, 2), nullable=False)
    tax_percent = Column(Numeric(5, 2), default=19.0)
    subtotal    = Column(Numeric(18, 2), nullable=False)
    quote       = relationship("Quote", back_populates="items")