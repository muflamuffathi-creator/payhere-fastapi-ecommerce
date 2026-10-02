import re
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService:
    @staticmethod
    def slugify(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        text = re.sub(r'^-+|-+$', '', text)
        return text

    @classmethod
    def get_products(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> List[Product]:
        query = db.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) | 
                (Product.description.ilike(f"%{search}%"))
            )
        return query.offset(skip).limit(limit).all()

    @classmethod
    def get_product_by_id(cls, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @classmethod
    def get_product_by_slug(cls, db: Session, slug: str) -> Optional[Product]:
        return db.query(Product).filter(Product.slug == slug).first()

    @classmethod
    def create_product(cls, db: Session, product_data: ProductCreate) -> Product:
        slug = product_data.slug or cls.slugify(product_data.name)
        # Check uniqueness
        counter = 1
        base_slug = slug
        while db.query(Product).filter(Product.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        db_product = Product(
            name=product_data.name,
            slug=slug,
            description=product_data.description,
            category=product_data.category,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            image_url=product_data.image_url,
            badge=product_data.badge,
            is_active=product_data.is_active
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @classmethod
    def update_product(cls, db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        db_product = cls.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        update_dict = product_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
        return db_product

    @classmethod
    def delete_product(cls, db: Session, product_id: int) -> bool:
        db_product = cls.get_product_by_id(db, product_id)
        if not db_product:
            return False
        db.delete(db_product)
        db.commit()
        return True
