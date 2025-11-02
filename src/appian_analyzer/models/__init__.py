from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from enum import Enum

class ComplexityLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

class ApplicationType(Enum):
    PROCESS_CENTRIC = "Process-Centric"
    DATA_CENTRIC = "Data-Centric"
    HYBRID = "Hybrid"
    PORTAL = "Portal"

@dataclass
class DataType:
    name: str
    fields: List[Dict[str, Any]]
    namespace: str
    business_domain: str
    complexity_score: int
    relationships: List[str] = field(default_factory=list)

@dataclass
class ProcessModel:
    name: str
    uuid: str
    nodes: List[Dict[str, Any]]
    roles: List[str]
    automation_level: str
    business_functions: List[str]
    complexity_score: int

@dataclass
class IntegrationPoint:
    name: str
    type: str
    pattern: str
    security_level: str
    endpoints: List[str] = field(default_factory=list)

@dataclass
class SecurityGroup:
    name: str
    uuid: str
    type: str
    business_function: str
    member_count: int = 0

@dataclass
class ApplicationBlueprint:
    # Core Information
    name: str
    description: str
    version: str
    complexity: ComplexityLevel
    app_type: ApplicationType
    
    # Detailed Analysis
    data_types: List[DataType] = field(default_factory=list)
    process_models: List[ProcessModel] = field(default_factory=list)
    integrations: List[IntegrationPoint] = field(default_factory=list)
    security_groups: List[SecurityGroup] = field(default_factory=list)
    
    # Metrics
    total_objects: int = 0
    maintainability_score: str = "Unknown"
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "application_info": {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "type": self.app_type.value,
                "complexity": self.complexity.value,
                "total_objects": self.total_objects,
                "maintainability": self.maintainability_score
            },
            "data_architecture": {
                "data_types": [
                    {
                        "name": dt.name,
                        "field_count": len(dt.fields),
                        "business_domain": dt.business_domain,
                        "complexity": dt.complexity_score,
                        "relationships": dt.relationships
                    } for dt in self.data_types
                ],
                "total_types": len(self.data_types),
                "avg_complexity": sum(dt.complexity_score for dt in self.data_types) / len(self.data_types) if self.data_types else 0
            },
            "business_processes": {
                "processes": [
                    {
                        "name": pm.name,
                        "node_count": len(pm.nodes),
                        "automation_level": pm.automation_level,
                        "business_functions": pm.business_functions,
                        "complexity": pm.complexity_score
                    } for pm in self.process_models
                ],
                "total_processes": len(self.process_models)
            },
            "integrations": {
                "systems": [
                    {
                        "name": ip.name,
                        "type": ip.type,
                        "pattern": ip.pattern,
                        "security_level": ip.security_level
                    } for ip in self.integrations
                ],
                "total_integrations": len(self.integrations)
            },
            "security": {
                "groups": [
                    {
                        "name": sg.name,
                        "type": sg.type,
                        "business_function": sg.business_function
                    } for sg in self.security_groups
                ],
                "total_groups": len(self.security_groups)
            },
            "recommendations": self.recommendations
        }
