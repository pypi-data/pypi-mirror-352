
from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
    model_validator,
)
from typing import Optional, Union, List, Dict, Any, Callable, Collection, Literal


class CelltypeMapCellTypeModel(BaseModel):
    """Input schema for mapping cluster IDs to cell type names."""
    cluster_key: str = Field(
        description="Key in adata.obs containing cluster IDs."
    )
    added_key: str = Field(
        description="Key to add to adata.obs for cell type names."
    )
    mapping: Dict[str, str] = Field(
        default=None,
        description="Mapping Dictionary from cluster IDs to cell type names."
    )
    new_names: Optional[List[str]] = Field(
        default=None,
        description="a list of new cell type names."
    )
