import uuid
from app.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import Column, DateTime, func, String
from app.utils.constants import PAGE_SIZE


def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @classmethod
    def get_all(
        cls,
        db: Session,
        sort_by: str = "created_at",
        order: str = "asc",
        min_date: str = None,
        max_date: str = None,
        min_value: int = None,
        max_value: int = None,
        search_field: str = None,
        search: str = None,
    ):
        query = db.query(cls)
        if min_date:
            query = query.filter(cls.created_at >= min_date)
        if max_date:
            query = query.filter(cls.created_at <= max_date)
        if min_value:
            query = query.filter(cls.value >= min_value)
        if max_value:
            query = query.filter(cls.value <= max_value)
        if search_field and search:
            query = query.filter(getattr(cls, search_field).ilike(f"%{search}%"))
        if order == "desc":
            query = query.order_by(getattr(cls, sort_by).desc())
        else:
            query = query.order_by(getattr(cls, sort_by).asc())

        instances = query.all()
        return [instance.to_dict() for instance in instances]

    @classmethod
    def get_paginated(
        cls,
        db: Session,
        page: int = 1,
        limit: int = PAGE_SIZE,
        sort_by: str = "created_at",
        order: str = "asc",
        min_date: str = None,
        max_date: str = None,
        min_value: int = None,
        max_value: int = None,
        search_field: str = None,
        search: str = None,
    ):
        query = db.query(cls)
        if min_date:
            query = query.filter(cls.created_at >= min_date)
        if max_date:
            query = query.filter(cls.created_at <= max_date)
        if min_value:
            query = query.filter(cls.value >= min_value)
        if max_value:
            query = query.filter(cls.value <= max_value)
        if search_field and search:
            query = query.filter(getattr(cls, search_field).ilike(f"%{search}%"))
        if order == "desc":
            query = query.order_by(getattr(cls, sort_by).desc())
        else:
            query = query.order_by(getattr(cls, sort_by).asc())

        instances = db.query(cls).limit(limit).offset((page - 1) * limit).all()
        return [instance.to_dict() for instance in instances]

    @classmethod
    def get_pagination_metadata(
        cls,
        db: Session,
        page: int = 1,
        limit: int = PAGE_SIZE,
        sort_by: str = "created_at",
        order: str = "asc",
        min_date: str = None,
        max_date: str = None,
        min_value: int = None,
        max_value: int = None,
        search_field: str = None,
        search: str = None,
    ):
        query = db.query(cls)
        if min_date:
            query = query.filter(cls.created_at >= min_date)
        if max_date:
            query = query.filter(cls.created_at <= max_date)
        if min_value:
            query = query.filter(cls.value >= min_value)
        if max_value:
            query = query.filter(cls.value <= max_value)
        if search_field and search:
            query = query.filter(getattr(cls, search_field).ilike(f"%{search}%"))
        if order == "desc":
            query = query.order_by(getattr(cls, sort_by).desc())
        else:
            query = query.order_by(getattr(cls, sort_by).asc())

        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        return dict(
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
        )

    @classmethod
    def get_by_id(cls, instance_id: str, db: Session):
        instance = db.query(cls).filter(cls.id == instance_id).first()
        return instance.to_dict() if instance else None

    @classmethod
    def create(cls, db: Session, **kwargs):
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance.to_dict()

    @classmethod
    def update(cls, instance_id: str, db: Session, **kwargs):
        instance = db.query(cls).filter(cls.id == instance_id).first()
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.commit()
            db.refresh(instance)
            return instance.to_dict()
        else:
            return None

    @classmethod
    def delete(cls, instance_id: str, db: Session):
        instance = db.query(cls).filter(cls.id == instance_id).first()
        if instance:
            db.delete(instance)
            db.commit()
            return True
        else:
            return False
