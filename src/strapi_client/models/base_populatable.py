from pydantic import BaseModel


class BasePopulatable(BaseModel):
    """Strapi entry that can be populated in request."""
