"""
Models for processing providers.
"""
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator, root_validator
from mindbank_poc.core.common.types import ProviderType


class MetadataCondition(BaseModel):
    """Condition for checking metadata."""
    key: str = Field(..., description="Metadata key to check")
    operator: Literal["eq", "neq", "contains", "gt", "lt", "gte", "lte", "in"] = Field(
        default="eq", 
        description="Comparison operator: eq (equals), neq (not equals), contains, gt (greater than), lt (less than), etc."
    )
    value: Any = Field(..., description="Value to compare against")


class ProviderFilter(BaseModel):
    """Filter for processing provider selection."""
    name: Optional[str] = Field(default=None, description="Filter name")
    archetypes: Optional[List[str]] = Field(default=None, description="List of supported archetypes")
    sources: Optional[List[str]] = Field(default=None, description="List of supported sources")
    metadata_conditions: Optional[List[MetadataCondition]] = Field(default=None, description="Metadata conditions")
    priority: int = Field(default=0, description="Filter priority (higher value means higher priority)")
    config_override: Optional[Dict[str, Any]] = Field(default=None, description="Configuration override for this filter")
    
    @validator('archetypes', 'sources', 'metadata_conditions', pre=True)
    def empty_list_to_none(cls, v):
        if isinstance(v, list) and len(v) == 0:
            return None
        return v


class ProviderModel(BaseModel):
    """Processing provider model."""
    id: str = Field(..., description="Unique provider ID")
    name: str = Field(..., description="Provider name")
    description: str = Field(..., description="Provider description")
    provider_type: ProviderType = Field(..., description="Provider type")
    supported_archetypes: List[str] = Field(default_factory=list, description="Supported archetypes")
    config_schema: Dict[str, Any] = Field(default_factory=dict, description="Configuration schema")
    current_config: Dict[str, Any] = Field(default_factory=dict, description="Current configuration")
    status: str = Field(default="active", description="Provider status")
    capabilities: List[str] = Field(default_factory=list, description="Provider capabilities")
    filters: List[ProviderFilter] = Field(default_factory=list, description="Filters for provider selection")
    instance: Optional[Any] = Field(default=None, description="Provider instance (not serialized)")
    
    class Config:
        """Pydantic configuration options"""
        # Exclude instance from serialization
        json_encoders = {
            # Handle the provider instance
            object: lambda obj: None if hasattr(obj, '__call__') else str(obj)
        }
        
    def dict(self, *args, **kwargs):
        """Override dict method to exclude the instance attribute"""
        if 'exclude' not in kwargs:
            kwargs['exclude'] = set()
        if isinstance(kwargs['exclude'], set):
            kwargs['exclude'].add('instance')
        return super().dict(*args, **kwargs) 