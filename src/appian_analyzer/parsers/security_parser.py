from typing import List
from pathlib import Path
from ..models import SecurityGroup
from . import BaseParser

class SecurityParser(BaseParser):
    """Parser for Security Groups and Roles"""
    
    def parse(self) -> List[SecurityGroup]:
        """Parse all security groups"""
        group_dir = self.extract_dir / "group"
        if not group_dir.exists():
            return []
        
        groups = []
        for xml_file in group_dir.glob("*.xml"):
            group = self._parse_group_file(xml_file)
            if group:
                groups.append(group)
        
        return groups
    
    def _parse_group_file(self, xml_file: Path) -> SecurityGroup:
        """Parse a single group file"""
        root = self.safe_parse_xml(xml_file)
        if root is None:
            return None
        
        name = self.get_text(root, ".//name", xml_file.stem)
        uuid = self.get_text(root, ".//uuid")
        description = self.get_text(root, ".//description")
        
        # Classify group type
        group_type = self._classify_group_type(name, description)
        
        # Infer business function
        business_function = self._infer_business_function(name, description)
        
        # Count members (if available)
        member_count = self._count_members(root)
        
        return SecurityGroup(
            name=name,
            uuid=uuid,
            type=group_type,
            business_function=business_function,
            member_count=member_count
        )
    
    def _classify_group_type(self, name: str, description: str) -> str:
        """Classify the type of security group"""
        name_lower = name.lower()
        desc_lower = description.lower() if description else ""
        
        # Administrative groups
        if any(keyword in name_lower for keyword in ["admin", "administrator", "system"]):
            return "Administrative"
        
        # Viewer/Read-only groups
        if any(keyword in name_lower for keyword in ["viewer", "read", "readonly", "view"]):
            return "Read-Only"
        
        # Editor/Contributor groups
        if any(keyword in name_lower for keyword in ["editor", "contributor", "author", "writer"]):
            return "Editor"
        
        # Manager groups
        if any(keyword in name_lower for keyword in ["manager", "lead", "supervisor"]):
            return "Manager"
        
        # Developer groups
        if any(keyword in name_lower for keyword in ["developer", "dev", "designer"]):
            return "Developer"
        
        # End user groups
        if any(keyword in name_lower for keyword in ["user", "member", "participant"]):
            return "End User"
        
        # Service/System groups
        if any(keyword in name_lower for keyword in ["service", "system", "process", "auto"]):
            return "System"
        
        return "Functional"
    
    def _infer_business_function(self, name: str, description: str) -> str:
        """Infer business function from group name and description"""
        text = f"{name} {description or ''}".lower()
        
        # Business function mapping
        function_keywords = {
            "Requirements Management": ["requirement", "rm", "req", "specification"],
            "Project Management": ["project", "pm", "portfolio"],
            "Financial Management": ["finance", "budget", "cost", "accounting"],
            "Human Resources": ["hr", "human", "employee", "personnel"],
            "IT Administration": ["it", "admin", "system", "infrastructure"],
            "Quality Assurance": ["qa", "quality", "test", "audit"],
            "Sales": ["sales", "crm", "customer"],
            "Operations": ["ops", "operations", "production"],
            "Security": ["security", "sec", "compliance"],
            "Reporting": ["report", "analytics", "dashboard"]
        }
        
        for function, keywords in function_keywords.items():
            if any(keyword in text for keyword in keywords):
                return function
        
        return "General"
    
    def _count_members(self, root) -> int:
        """Count group members if information is available"""
        # Look for member elements
        members = self.find_all(root, ".//member") + self.find_all(root, ".//user")
        return len(members)
