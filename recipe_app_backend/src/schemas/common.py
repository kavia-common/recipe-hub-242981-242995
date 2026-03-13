"""Common schema utilities."""

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base schema enabling ORM mode."""

    model_config = ConfigDict(from_attributes=True)
