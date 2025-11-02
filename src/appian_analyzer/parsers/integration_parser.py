from typing import List
from pathlib import Path
from ..models import IntegrationPoint
from . import BaseParser

class IntegrationParser(BaseParser):
    """Parser for Connected Systems and Web APIs"""
    
    def parse(self) -> List[IntegrationPoint]:
        """Parse all integration points"""
        integrations = []
        
        # Parse Connected Systems
        integrations.extend(self._parse_connected_systems())
        
        # Parse Web APIs
        integrations.extend(self._parse_web_apis())
        
        return integrations
    
    def _parse_connected_systems(self) -> List[IntegrationPoint]:
        """Parse connected systems"""
        cs_dir = self.extract_dir / "connectedSystem"
        if not cs_dir.exists():
            return []
        
        systems = []
        for xml_file in cs_dir.glob("*.xml"):
            system = self._parse_connected_system_file(xml_file)
            if system:
                systems.append(system)
        
        return systems
    
    def _parse_connected_system_file(self, xml_file: Path) -> IntegrationPoint:
        """Parse a single connected system file"""
        root = self.safe_parse_xml(xml_file)
        if root is None:
            return None
        
        name = self.get_text(root, ".//name", xml_file.stem)
        system_type = self.get_text(root, ".//type", "Unknown")
        description = self.get_text(root, ".//description")
        
        # Determine integration pattern
        pattern = self._determine_integration_pattern(system_type, description)
        
        # Assess security level
        security_level = self._assess_security_level(system_type, root)
        
        # Extract endpoints if available
        endpoints = self._extract_endpoints(root)
        
        return IntegrationPoint(
            name=name,
            type=f"Connected System - {system_type}",
            pattern=pattern,
            security_level=security_level,
            endpoints=endpoints
        )
    
    def _parse_web_apis(self) -> List[IntegrationPoint]:
        """Parse web APIs"""
        api_dir = self.extract_dir / "webApi"
        if not api_dir.exists():
            return []
        
        apis = []
        for xml_file in api_dir.glob("*.xml"):
            api = self._parse_web_api_file(xml_file)
            if api:
                apis.append(api)
        
        return apis
    
    def _parse_web_api_file(self, xml_file: Path) -> IntegrationPoint:
        """Parse a single web API file"""
        root = self.safe_parse_xml(xml_file)
        if root is None:
            return None
        
        name = self.get_text(root, ".//name", xml_file.stem)
        description = self.get_text(root, ".//description")
        
        # Extract HTTP methods and endpoints
        endpoints = self._extract_api_endpoints(root)
        
        # Determine security configuration
        security_level = self._assess_api_security(root)
        
        return IntegrationPoint(
            name=name,
            type="Web API",
            pattern="REST API",
            security_level=security_level,
            endpoints=endpoints
        )
    
    def _determine_integration_pattern(self, system_type: str, description: str) -> str:
        """Determine integration pattern from system type"""
        type_lower = system_type.lower()
        desc_lower = description.lower() if description else ""
        
        pattern_mapping = {
            "REST": ["rest", "http", "json"],
            "SOAP": ["soap", "wsdl", "xml"],
            "Database": ["database", "jdbc", "sql", "oracle", "mysql"],
            "File System": ["file", "ftp", "sftp"],
            "Message Queue": ["queue", "jms", "mq"],
            "Cloud Service": ["aws", "azure", "gcp", "cloud"],
            "Custom": ["custom", "proprietary"]
        }
        
        for pattern, keywords in pattern_mapping.items():
            if any(keyword in type_lower or keyword in desc_lower for keyword in keywords):
                return pattern
        
        return "Unknown"
    
    def _assess_security_level(self, system_type: str, root) -> str:
        """Assess security level of the integration"""
        # Look for authentication configuration
        auth_elements = self.find_all(root, ".//authentication") + self.find_all(root, ".//security")
        
        if auth_elements:
            # Check for specific auth types
            auth_text = " ".join(elem.text or "" for elem in auth_elements).lower()
            
            if any(keyword in auth_text for keyword in ["oauth", "jwt", "certificate"]):
                return "High"
            elif any(keyword in auth_text for keyword in ["basic", "api_key"]):
                return "Medium"
            else:
                return "Low"
        
        # Default assessment based on type
        type_lower = system_type.lower()
        if "database" in type_lower or "internal" in type_lower:
            return "High"
        elif "http" in type_lower or "rest" in type_lower:
            return "Medium"
        else:
            return "Unknown"
    
    def _assess_api_security(self, root) -> str:
        """Assess Web API security configuration"""
        # Look for security configurations
        security_elements = self.find_all(root, ".//security") + self.find_all(root, ".//authentication")
        
        if security_elements:
            return "Configured"
        else:
            return "Basic"
    
    def _extract_endpoints(self, root) -> List[str]:
        """Extract endpoint URLs from connected system"""
        endpoints = []
        
        # Look for URL configurations
        url_elements = self.find_all(root, ".//url") + self.find_all(root, ".//endpoint")
        for elem in url_elements:
            if elem.text:
                endpoints.append(elem.text.strip())
        
        return endpoints
    
    def _extract_api_endpoints(self, root) -> List[str]:
        """Extract API endpoints and methods"""
        endpoints = []
        
        # Look for HTTP method configurations
        method_elements = self.find_all(root, ".//httpMethod") + self.find_all(root, ".//method")
        path_elements = self.find_all(root, ".//path") + self.find_all(root, ".//endpoint")
        
        methods = [elem.text.strip() for elem in method_elements if elem.text]
        paths = [elem.text.strip() for elem in path_elements if elem.text]
        
        # Combine methods and paths
        if methods and paths:
            for method in methods:
                for path in paths:
                    endpoints.append(f"{method} {path}")
        elif paths:
            endpoints.extend(paths)
        elif methods:
            endpoints.extend(methods)
        
        return endpoints
