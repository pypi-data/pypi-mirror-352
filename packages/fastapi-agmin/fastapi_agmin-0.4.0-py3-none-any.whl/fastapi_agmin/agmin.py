import logging
from datetime import date, datetime, time
from decimal import Decimal
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, cast

import yaml
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy import Date, String, or_, select
from sqlalchemy import Enum as SAEnum
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeMeta, Mapper, Session, selectinload

DISPLAY_NAME_FIELD = "display_name_"

MAX_RECORDS = 1000


def create_agmin(
    base: DeclarativeMeta,
    get_session: Callable[[], Session],
    app: Optional[FastAPI] = None,
    home_url: str = "/",
    ignored_columns: Optional[List[str]] = None,
) -> "SQLAlchemyAgmin":
    """Create and configure a SQLAlchemyAgmin instance.

    Args:
        base: SQLAlchemy declarative base containing model definitions
        get_session: Callable that returns a SQLAlchemy session
        app: Optional FastAPI application instance

    Returns:
        SQLAlchemyAgmin: Configured admin interface instance
    """
    return SQLAlchemyAgmin(base, get_session, app, home_url=home_url, ignored_columns=ignored_columns)


# Configure logging filter
class StaticAssetFilter(logging.Filter):
    def filter(self, record):
        # Filter out static asset requests from uvicorn access logs
        if record.getMessage().startswith('"GET /assets/') or record.getMessage().startswith('"GET /static/'):
            return False

        # Filter out response body logs for static assets
        if "Response body:" in record.getMessage() and (
            "/assets/" in record.getMessage() or "/static/" in record.getMessage()
        ):
            return False

        return True


# Apply filter to both uvicorn access logger and test_app logger
logging.getLogger("uvicorn.access").addFilter(StaticAssetFilter())
logging.getLogger("test_app").addFilter(StaticAssetFilter())


class SQLAlchemyAgmin:
    def __init__(
        self,
        base: DeclarativeMeta,
        get_session,
        app: Optional[FastAPI] = None,
        home_url: str = "/",
        ignored_columns: Optional[List[str]] = None,
    ):
        # base is sqlalchemy.orm.declarative_base
        self.base = base
        self.get_session = get_session  # FastAPI dependency for DB session
        self.app = app
        self.home_url = home_url
        self.ignored_columns = ignored_columns or []

        # Build a name → model class map using SQLAlchemy 2.x compatible approach
        self.model_map = {mapper.class_.__name__.lower(): mapper.class_ for mapper in self.base.registry.mappers}

        # If app is provided, set up routes and static files
        if app is not None:
            self._setup_app(app)

    def _get_static_dir(self) -> Path:
        """Get the path to the static directory in the installed package."""
        return resources.files("fastapi_agmin").joinpath("static")

    def _setup_app(self, app: FastAPI):
        """Set up routes and static files for the FastAPI app."""
        # Include the API router
        app.include_router(self.create_fastapi_router(), prefix="/agmin/api")

        # Get the static directory path
        static_dir = self._get_static_dir()

        # Serve the Vue app's assets directory
        app.mount(
            "/assets",
            StaticFiles(directory=str(static_dir / "assets")),
            name="assets",
        )

        # Handle all /agmin/* routes
        @app.get("/agmin/{path:path}")
        async def admin_page(path: str = ""):
            if path.startswith("assets/"):
                # Let the static files handler take care of assets
                return RedirectResponse(url=f"/assets/{path[7:]}")

            # For any other path, serve index.html with next parameter
            if path:
                return RedirectResponse(url=f"/agmin/?next=/agmin/{path}")

            # For /agmin/, serve index.html directly
            return FileResponse(str(static_dir / "index.html"))

    def _serialize_instance(self, instance: Any, depth: int = 0) -> Dict[str, Any] | None:
        """Serialize a SQLAlchemy instance to a dictionary."""
        if instance is None:
            return None

        # Prevent infinite recursion
        if depth > 2:
            return {"id": getattr(instance, "id", None), DISPLAY_NAME_FIELD: str(instance)}

        data = {}
        mapper = sa_inspect(instance.__class__)

        # Add DISPLAY_NAME_FIELD field
        data[DISPLAY_NAME_FIELD] = str(instance)

        # Add columns
        for column in mapper.columns:
            value = getattr(instance, column.key)
            if isinstance(value, (date, datetime, time)):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = str(value)
            data[column.key] = value

        # Add relationships
        for rel in mapper.relationships:
            value = getattr(instance, rel.key)
            if value is not None:
                if rel.uselist:
                    data[rel.key] = [self._serialize_instance(item, depth + 1) for item in value]
                else:
                    data[rel.key] = self._serialize_instance(value, depth + 1)
            else:
                data[rel.key] = None

        return data

    @lru_cache(maxsize=1)  # noqa: B019
    def generate_metadata(self) -> Dict[str, Any]:
        metadata = {}
        for cls in self.base.registry.mappers:
            if isinstance(cls.class_, type) and hasattr(cls.class_, "__tablename__"):
                model_info = {
                    "table": cls.class_.__tablename__,
                    "columns": {},
                    "relationships": {},
                }
                mapper = sa_inspect(cls.class_)
                # Add synthetic display_name_ column
                model_info["columns"][DISPLAY_NAME_FIELD] = {
                    "type": "VARCHAR",
                    "nullable": False,
                    "primary_key": False,
                    "unique": False,
                    "enum_values": None,
                    "label": "Display Name",
                    "help_text": "Human-readable display name for this row",
                }

                # Get foreign key columns from relationships
                fk_columns = set()
                for rel in mapper.relationships:
                    for col in rel.local_columns:
                        fk_columns.add(col.name)

                # Columns
                for column in mapper.columns:
                    # Skip columns that are foreign keys in relationships
                    if (column.name in fk_columns) or (column.name in self.ignored_columns):
                        continue

                    col_type = str(column.type)
                    enum_values = None
                    if isinstance(column.type, SAEnum):
                        enum_values = list(column.type.enums)

                    model_info["columns"][column.name] = {
                        "type": col_type,
                        "nullable": column.nullable,
                        "primary_key": column.primary_key,
                        "unique": column.unique,
                        "enum_values": enum_values,
                        "label": getattr(column, "info", {}).get("label"),
                        "help_text": getattr(column, "info", {}).get("help_text"),
                    }

                # Relationships
                for rel in mapper.relationships:
                    rel_type = (
                        "many_to_one"
                        if rel.direction.name == "MANYTOONE"
                        else (
                            "one_to_many"
                            if rel.direction.name == "ONETOMANY"
                            else ("many_to_many" if rel.direction.name == "MANYTOMANY" else "unknown")
                        )
                    )
                    local_cols = [col.name for col in rel.local_columns]
                    remote_cols = [col.name for col in rel.remote_side]

                    # Generate a descriptive label for the relationship
                    # This is especially important for self-referential relationships
                    # where both sides point to the same model class
                    target_class_name = rel.mapper.class_.__name__

                    # Determine if this relationship is self-referential (points to the same model)
                    is_self_referential = cls.class_.__name__ == target_class_name

                    # Create a meaningful label for the relationship
                    if rel.key:
                        # Convert from snake_case to Title Case for display
                        relationship_label = " ".join(word.capitalize() for word in rel.key.split("_"))
                    else:
                        relationship_label = target_class_name

                    # For self-referential relationships, ensure the label is clear about the relationship direction
                    if is_self_referential:
                        # Check for common relationship patterns
                        if any(word in rel.key for word in ["parent", "requirement"]):
                            relationship_label = f"{relationship_label} (Parent)"
                        elif any(word in rel.key for word in ["child", "dependent"]):
                            relationship_label = f"{relationship_label} (Child)"
                        # If we can't determine the direction, use the local and remote column names
                        else:
                            local_col_name = local_cols[0] if local_cols else "this"
                            remote_col_name = remote_cols[0] if remote_cols else "other"
                            relationship_label = f"{relationship_label} ({local_col_name} → {remote_col_name})"

                    relationship_info = {
                        "type": rel_type,
                        "target": target_class_name,
                        "back_populates": rel.back_populates,
                        "secondary": (rel.secondary.name if rel.secondary is not None else None),
                        "local_columns": local_cols,
                        "remote_columns": remote_cols,
                        "label": relationship_label,  # Add custom label for UI display
                    }
                    model_info["relationships"][rel.key] = relationship_info

                metadata[cls.class_.__name__] = model_info

        return {"models": metadata}

    def _create_pydantic_model(
        self,
        cls: Type,
        include_relationships: bool = False,
        exclude_readonly: bool = False,
    ) -> Type[BaseModel]:
        """
        Dynamically create a Pydantic model from a SQLAlchemy model.

        :param cls: SQLAlchemy model class
        :param include_relationships: Whether to include relationships in the model
        :param exclude_readonly: Whether to exclude read-only fields (e.g., primary keys)
        :return: Pydantic model class
        """
        fields = {}
        mapper = sa_inspect(cls)

        # Add DISPLAY_NAME_FIELD field for display
        fields[DISPLAY_NAME_FIELD] = (str, "")

        # Add columns
        for column in mapper.columns:
            if exclude_readonly and column.primary_key:
                continue
            if column.key in self.ignored_columns:
                continue
            python_type = column.type.python_type
            if column.nullable:
                python_type = Optional[python_type]
            fields[column.key] = (python_type, None if column.nullable else ...)

        # Add relationships if required
        if include_relationships:
            for rel in mapper.relationships:
                if rel.uselist:
                    fields[rel.key] = (List[Any], [])
                else:
                    fields[rel.key] = (Optional[Dict[str, Any]], None)

        return create_model(
            f"{cls.__name__}Model",
            **fields,
            __config__=ConfigDict(from_attributes=True),
        )

    def create_fastapi_router(self) -> APIRouter:
        router = APIRouter()
        db_dependency = Depends(self.get_session)

        @router.get("/metadata", response_model=Dict[str, Any])
        async def get_metadata(format: str = Query("json", enum=["json", "yaml"])):  # noqa: A002
            metadata = self.generate_metadata()
            metadata["home_url"] = self.home_url  # Include home_url in metadata
            if format == "yaml":
                yaml_str = yaml.dump(metadata, sort_keys=False, allow_unicode=True)
                return Response(content=yaml_str, media_type="application/x-yaml")
            else:
                return JSONResponse(content=metadata)

        @router.get("/{model}/search")
        async def search_items(
            model: str,
            q: str = Query(..., min_length=3),
            db: Session = db_dependency,
        ) -> List[Dict[str, Any]]:
            cls = self._get_model(model)
            mapper = sa_inspect(cls)

            # Build search conditions for string columns
            conditions = []
            for column in mapper.columns:
                if isinstance(column.type, (String, Date)):
                    conditions.append(column.ilike(f"%{q}%"))

            if not conditions:
                return []

            query = select(cls).where(or_(*conditions)).limit(MAX_RECORDS)
            items = db.scalars(query).all()

            # Format results using __str__ method
            return [{"id": item.id, "label": str(item)} for item in items]

        @router.get("/{model}")
        async def list_items(
            model: str,
            db: Session = db_dependency,
            request: Request = None,
        ) -> List[Dict[str, Any]]:
            filters = dict(request.query_params)
            cls = self._get_model(model)
            output_model = self._create_pydantic_model(cls, include_relationships=True)
            query = select(cls)
            mapper = sa_inspect(cls)
            # Foreign key filtering
            for rel in mapper.relationships:
                rel_param = f"{rel.key}_id"
                if rel_param in filters and filters[rel_param] is not None:
                    try:
                        fk_id = int(filters[rel_param])
                    except Exception:
                        continue
                    # For many-to-one, filter by foreign key column
                    if rel.direction.name == "MANYTOONE":
                        fk_col = list(rel.local_columns)[0]
                        query = query.where(fk_col == fk_id)
                    # For one-to-many, filter by existence of related row
                    elif rel.direction.name == "ONETOMANY":
                        related_cls = rel.mapper.class_
                        # Use rel.primaryjoin to get the join condition between parent and related
                        join_cond = rel.primaryjoin
                        subq = select(1).where((related_cls.id == fk_id) & join_cond).exists()
                        query = query.where(subq)
                    # For many-to-many, skip for now
            for rel in mapper.relationships:
                query = query.options(selectinload(getattr(cls, rel.key)))
            query = query.limit(MAX_RECORDS)
            items = db.scalars(query).all()
            result = [output_model.model_validate(self._serialize_instance(item)).model_dump() for item in items]
            return result

        @router.get("/{model}/{item_id}")
        async def get_item(
            model: str,
            item_id: int,
            db: Session = db_dependency,
        ) -> Dict[str, Any]:
            cls = self._get_model(model)
            output_model = self._create_pydantic_model(cls, include_relationships=True)

            # Build query with eager loading for all relationships
            query = select(cls).where(cls.id == item_id)
            for rel in sa_inspect(cls).relationships:
                # Load all relationships eagerly
                query = query.options(selectinload(getattr(cls, rel.key)))

            item = db.scalars(query).first()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            result = output_model.model_validate(self._serialize_instance(item)).model_dump()
            result[DISPLAY_NAME_FIELD] = str(item)
            return result

        @router.post("/{model}")
        async def create_item(
            model: str,
            payload: Dict[str, Any],
            db: Session = db_dependency,
        ) -> Dict[str, Any]:
            cls = self._get_model(model)
            input_model = self._create_pydantic_model(cls, exclude_readonly=True)
            output_model = self._create_pydantic_model(cls, include_relationships=True)
            validated_data = input_model(**payload)
            item = cls()

            # Handle relationships first
            mapper = sa_inspect(cls)
            for rel in mapper.relationships:
                if rel.key in validated_data.model_dump():
                    value = validated_data.model_dump()[rel.key]
                    if value is not None:
                        related_cls = rel.mapper.class_
                        if rel.uselist:
                            related_objs = db.query(related_cls).filter(related_cls.id.in_(value)).all()
                            setattr(item, rel.key, related_objs)
                        else:
                            related_obj = db.get(cast(Mapper, related_cls), value)
                            setattr(item, rel.key, related_obj)

            # Handle regular fields
            for key, value in validated_data.model_dump().items():
                if key not in [rel.key for rel in mapper.relationships]:
                    setattr(item, key, value)

            db.add(item)
            db.commit()
            db.refresh(item)
            return output_model.model_validate(self._serialize_instance(item)).model_dump()

        @router.put("/{model}/{item_id}")
        async def update_item(
            model: str,
            item_id: int,
            payload: Dict[str, Any],
            db: Session = db_dependency,
        ) -> Dict[str, Any]:
            cls = self._get_model(model)
            input_model = self._create_pydantic_model(cls, exclude_readonly=True)
            output_model = self._create_pydantic_model(cls, include_relationships=True)
            validated_data = input_model(**payload)
            item = db.get(cast(Mapper, cls), item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")

            try:
                # Handle relationships first
                mapper = sa_inspect(cls)
                for rel in mapper.relationships:
                    if rel.key in validated_data.model_dump():
                        value = validated_data.model_dump()[rel.key]
                        if value is not None:
                            related_cls = rel.mapper.class_
                            if rel.uselist:
                                related_objs = db.query(related_cls).filter(related_cls.id.in_(value)).all()
                                setattr(item, rel.key, related_objs)
                            else:
                                related_obj = db.get(cast(Mapper, related_cls), value)
                                setattr(item, rel.key, related_obj)

                # Handle regular fields
                for key, value in validated_data.model_dump().items():
                    if key not in [rel.key for rel in mapper.relationships]:
                        setattr(item, key, value)

                db.commit()
                db.refresh(item)
                return output_model.model_validate(self._serialize_instance(item)).model_dump()
            except IntegrityError as e:
                db.rollback()
                error_msg = str(e.orig)
                if "CHECK constraint failed" in error_msg:
                    # Extract the field name from the error message
                    field_name = error_msg.split(":")[-1].strip()
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "loc": ["body", field_name],
                            "msg": f"Invalid value: {error_msg}",
                            "type": "value_error",
                        },
                    ) from e
                raise HTTPException(status_code=400, detail=str(e)) from e

        @router.delete("/{model}/{item_id}", response_model=Dict[str, str])
        async def delete_item(
            model: str,
            item_id: int,
            db: Session = db_dependency,
        ):
            cls = self._get_model(model)
            item = db.get(cast(Mapper, cls), item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            db.delete(item)
            db.commit()
            return {"detail": "Item deleted"}

        return router

    def _get_model(self, model_name: str):
        cls = self.model_map.get(model_name.lower())
        if not cls:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        return cls
