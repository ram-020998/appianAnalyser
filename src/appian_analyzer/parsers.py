"""
XML parsers for different Appian object types
"""
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from .models import AppianObject, Site, RecordType, ProcessModel, SimpleObject

class XMLParser(ABC):
    """Abstract base class for XML parsers"""
    
    def __init__(self):
        self.namespaces = {
            'a': 'http://www.appian.com/ae/types/2009',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the file"""
        pass
    
    @abstractmethod
    def parse(self, root: ET.Element, file_path: str) -> Optional[AppianObject]:
        """Parse XML and return Appian object"""
        pass
    
    def _get_element_text(self, parent: ET.Element, xpath: str) -> str:
        """Safely get element text"""
        elem = parent.find(xpath, self.namespaces)
        return elem.text.strip() if elem is not None and elem.text else ""

class SiteParser(XMLParser):
    """Parser for Site objects"""
    
    def can_parse(self, file_path: str) -> bool:
        return 'site/' in file_path
    
    def parse(self, root: ET.Element, file_path: str) -> Optional[Site]:
        site_elem = root.find('site')
        if site_elem is None:
            return None
        
        uuid = site_elem.get('{http://www.appian.com/ae/types/2009}uuid')
        name = site_elem.get('name')
        desc_elem = site_elem.find('description')
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        if not uuid or not name:
            return None
        
        site = Site(uuid=uuid, name=name, object_type="Site", description=description)
        site.pages = self._parse_pages(site_elem)
        site.security = self._parse_security(root)
        
        return site
    
    def _parse_pages(self, site_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse site pages"""
        pages = []
        for page_elem in site_elem.findall('page', self.namespaces):
            page_uuid = page_elem.get('{http://www.appian.com/ae/types/2009}uuid')
            static_name = self._get_element_text(page_elem, 'staticName')
            
            page_data = {
                "uuid": page_uuid,
                "name": static_name,
                "ui_objects": [],
                "visibility": self._get_element_text(page_elem, 'visibilityExpr')
            }
            
            ui_elem = page_elem.find('uiObject', self.namespaces)
            if ui_elem is not None:
                ui_uuid = ui_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                ui_type = ui_elem.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
                page_data["ui_objects"].append({
                    "uuid": ui_uuid,
                    "name": "Unknown",  # Will be resolved later
                    "type": ui_type.replace('a:', '') if ui_type else "Unknown"
                })
            
            pages.append(page_data)
        
        return pages
    
    def _parse_security(self, root: ET.Element) -> Dict[str, Any]:
        """Parse security from roleMap"""
        security = {"roles": []}
        for role_elem in root.findall('.//roleMap/role'):
            role_name = role_elem.get('name')
            users = [u.text for u in role_elem.findall('.//userUuid')]
            group_uuids = [g.text for g in role_elem.findall('.//groupUuid')]
            
            if users or group_uuids:
                security["roles"].append({
                    "role": role_name,
                    "users": users,
                    "groups": [{"uuid": g, "name": "Unknown"} for g in group_uuids]
                })
        
        return security

class RecordTypeParser(XMLParser):
    """Parser for Record Type objects"""
    
    def can_parse(self, file_path: str) -> bool:
        return 'recordType/' in file_path
    
    def parse(self, root: ET.Element, file_path: str) -> Optional[RecordType]:
        record_elem = root.find('recordType')
        if record_elem is None:
            return None
        
        uuid = record_elem.get('{http://www.appian.com/ae/types/2009}uuid')
        name = record_elem.get('name')
        desc_elem = record_elem.find('a:description', self.namespaces)
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        if not uuid or not name:
            return None
        
        record = RecordType(uuid=uuid, name=name, object_type="Record Type", description=description)
        record.fields = self._parse_fields(record_elem)
        record.relationships = self._parse_relationships(record_elem)
        record.actions = self._parse_actions(record_elem)
        record.views = self._parse_views(record_elem)
        record.security = {"roles": []}  # Simplified
        
        return record
    
    def _parse_fields(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record fields"""
        fields = []
        for field_elem in record_elem.findall('.//a:field', self.namespaces):
            field_data = {
                "name": self._get_element_text(field_elem, 'a:name'),
                "type": self._get_element_text(field_elem, 'a:type'),
                "required": self._get_element_text(field_elem, 'a:required') == 'true',
                "primary_key": self._get_element_text(field_elem, 'a:primaryKey') == 'true'
            }
            fields.append(field_data)
        return fields
    
    def _parse_relationships(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record relationships"""
        relationships = []
        for rel_elem in record_elem.findall('.//a:recordRelationshipCfg', self.namespaces):
            rel_data = {
                "uuid": self._get_element_text(rel_elem, 'a:uuid'),
                "name": self._get_element_text(rel_elem, 'a:relationshipName'),
                "target_record": {
                    "uuid": self._get_element_text(rel_elem, 'a:targetRecordTypeUuid'),
                    "name": "Unknown"
                }
            }
            relationships.append(rel_data)
        return relationships
    
    def _parse_actions(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record actions"""
        actions = []
        for action_elem in record_elem.findall('.//a:relatedActionCfg', self.namespaces):
            target_elem = action_elem.find('a:target', self.namespaces)
            target_uuid = target_elem.get('{http://www.appian.com/ae/types/2009}uuid') if target_elem is not None else None
            
            action_data = {
                "uuid": action_elem.get('{http://www.appian.com/ae/types/2009}uuid'),
                "title": self._get_element_text(action_elem, 'a:titleExpr'),
                "description": self._get_element_text(action_elem, 'a:descriptionExpr'),
                "target_process": {"uuid": target_uuid, "name": "Unknown"},
                "context": self._get_element_text(action_elem, 'a:contextExpr'),
                "visibility": self._get_element_text(action_elem, 'a:visibilityExpr'),
                "security": {}
            }
            actions.append(action_data)
        return actions
    
    def _parse_views(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record views"""
        views = []
        for view_elem in record_elem.findall('.//a:recordView', self.namespaces):
            view_data = {
                "name": self._get_element_text(view_elem, 'a:name'),
                "type": self._get_element_text(view_elem, 'a:type')
            }
            views.append(view_data)
        return views

class ProcessModelParser(XMLParser):
    """Parser for Process Model objects"""
    
    def can_parse(self, file_path: str) -> bool:
        return 'processModel/' in file_path
    
    def parse(self, root: ET.Element, file_path: str) -> Optional[ProcessModel]:
        pm_port = root.find('{http://www.appian.com/ae/types/2009}process_model_port')
        if pm_port is None:
            return None
        
        pm_elem = pm_port.find('{http://www.appian.com/ae/types/2009}pm')
        if pm_elem is None:
            return None
        
        meta_elem = pm_elem.find('{http://www.appian.com/ae/types/2009}meta')
        if meta_elem is None:
            return None
        
        uuid_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}uuid')
        name_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}name')
        desc_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}desc')
        
        uuid = uuid_elem.text if uuid_elem is not None and uuid_elem.text else None
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
        description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
        
        if not uuid:
            return None
        
        if not name:
            name = f"Process Model {uuid.split('-')[0]}"
        
        process = ProcessModel(uuid=uuid, name=name, object_type="Process Model", description=description)
        process.variables = self._parse_variables(pm_elem)
        process.nodes = self._parse_nodes(pm_elem)
        process.flows = self._parse_flows(pm_elem)
        process.security = self._parse_security(root)
        
        return process
    
    def _parse_variables(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse process variables"""
        variables = []
        for pv_elem in pm_elem.findall('.//pvs/pv'):
            var_data = {
                "name": self._get_element_text(pv_elem, 'name'),
                "type": self._get_element_text(pv_elem, 'type'),
                "parameter": self._get_element_text(pv_elem, 'parameter') == 'true',
                "multiple": self._get_element_text(pv_elem, 'multiple') == 'true'
            }
            variables.append(var_data)
        return variables
    
    def _parse_nodes(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse process nodes"""
        nodes = []
        for node_elem in pm_elem.findall('.//nodes/node'):
            node_data = {
                "uuid": node_elem.get('uuid'),
                "name": self._get_element_text(node_elem, 'name'),
                "type": self._determine_node_type(node_elem),
                "details": self._parse_node_details(node_elem)
            }
            nodes.append(node_data)
        return nodes
    
    def _parse_flows(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse process flows"""
        flows = []
        for flow_elem in pm_elem.findall('.//flows/flow'):
            flow_data = {
                "from": self._get_element_text(flow_elem, 'from'),
                "to": self._get_element_text(flow_elem, 'to'),
                "condition": self._get_element_text(flow_elem, 'condition')
            }
            flows.append(flow_data)
        return flows
    
    def _determine_node_type(self, node_elem: ET.Element) -> str:
        """Determine node type"""
        if node_elem.find('.//form-config') is not None:
            return "User Input Task"
        elif node_elem.find('.//expr') is not None:
            return "Script Task"
        elif node_elem.find('.//subprocess') is not None:
            return "Call Process"
        return "Unknown"
    
    def _parse_node_details(self, node_elem: ET.Element) -> Dict[str, Any]:
        """Parse node details"""
        details = {}
        form_config = node_elem.find('.//form-config')
        if form_config is not None:
            ui_expr = form_config.find('.//uiExpressionForm')
            if ui_expr is not None:
                details["interface"] = {"uuid": ui_expr.text, "name": "Unknown"}
        
        expr_elem = node_elem.find('.//expr')
        if expr_elem is not None:
            details["expression"] = expr_elem.text
        
        return details
    
    def _parse_security(self, root: ET.Element) -> Dict[str, Any]:
        """Parse process model security"""
        security = {"roles": []}
        role_map = root.find('roleMap')
        if role_map is not None:
            for role_elem in role_map.findall('role'):
                role_name = role_elem.get('name')
                users = [u.text for u in role_elem.findall('.//userUuid')]
                group_uuids = [g.text for g in role_elem.findall('.//groupUuid')]
                
                if users or group_uuids:
                    security["roles"].append({
                        "role": role_name,
                        "users": users,
                        "groups": [{"uuid": g, "name": "Unknown"} for g in group_uuids]
                    })
        return security

class ContentParser(XMLParser):
    """Parser for content objects (interfaces, rules, constants, etc.)"""
    
    def can_parse(self, file_path: str) -> bool:
        return 'content/' in file_path
    
    def parse(self, root: ET.Element, file_path: str) -> Optional[SimpleObject]:
        for child in root:
            if child.tag.endswith('Haul') or child.tag in ['versionUuid', 'roleMap', 'history', 'migrationVersion']:
                continue
            
            # Check for child elements (newer format)
            uuid_elem = child.find('uuid')
            name_elem = child.find('name')
            desc_elem = child.find('description')
            
            if uuid_elem is not None and name_elem is not None:
                uuid = uuid_elem.text
                name = name_elem.text
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                object_type = self._determine_content_type(child.tag)
                
                return SimpleObject(uuid=uuid, name=name, object_type=object_type, description=description)
        
        return None
    
    def _determine_content_type(self, tag: str) -> str:
        """Determine content object type"""
        type_mapping = {
            'interface': 'Interface',
            'rule': 'Expression Rule',
            'constant': 'Constant',
            'datatype': 'Data Type',
            'decision': 'Decision',
            'queryRule': 'Query Rule',
            'document': 'Document',
            'folder': 'Folder',
            'rulesFolder': 'Rules Folder',
            'communityKnowledgeCenter': 'Knowledge Center',
            'contentFreeformRule': 'Content Rule'
        }
        clean_tag = tag.split('}')[-1] if '}' in tag else tag
        return type_mapping.get(clean_tag, clean_tag)

class SimpleObjectParser(XMLParser):
    """Parser for simple objects (groups, connected systems, etc.)"""
    
    def __init__(self, object_type: str, path_pattern: str):
        super().__init__()
        self.object_type = object_type
        self.path_pattern = path_pattern
    
    def can_parse(self, file_path: str) -> bool:
        return self.path_pattern in file_path
    
    def parse(self, root: ET.Element, file_path: str) -> Optional[SimpleObject]:
        if self.object_type == "Security Group":
            return self._parse_group(root)
        elif self.object_type == "Connected System":
            return self._parse_connected_system(root)
        elif self.object_type == "Web API":
            return self._parse_web_api(root)
        elif self.object_type == "Report":
            return self._parse_report(root)
        return None
    
    def _parse_group(self, root: ET.Element) -> Optional[SimpleObject]:
        group_elem = root.find('group')
        if group_elem is None:
            return None
        
        uuid_elem = group_elem.find('uuid')
        name_elem = group_elem.find('name')
        desc_elem = group_elem.find('description')
        
        if uuid_elem is None or name_elem is None:
            return None
        
        return SimpleObject(
            uuid=uuid_elem.text,
            name=name_elem.text,
            object_type="Security Group",
            description=desc_elem.text if desc_elem is not None and desc_elem.text else ""
        )
    
    def _parse_connected_system(self, root: ET.Element) -> Optional[SimpleObject]:
        cs_elem = root.find('connectedSystem')
        if cs_elem is None:
            return None
        
        uuid = cs_elem.get('{http://www.appian.com/ae/types/2009}uuid')
        name = cs_elem.get('name')
        desc_elem = cs_elem.find('a:description', self.namespaces)
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        if not uuid or not name:
            return None
        
        return SimpleObject(uuid=uuid, name=name, object_type="Connected System", description=description)
    
    def _parse_web_api(self, root: ET.Element) -> Optional[SimpleObject]:
        api_elem = root.find('webApi')
        if api_elem is None:
            return None
        
        uuid = api_elem.get('{http://www.appian.com/ae/types/2009}uuid')
        name = api_elem.get('name')
        desc_elem = api_elem.find('a:description', self.namespaces)
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        if not uuid or not name:
            return None
        
        return SimpleObject(uuid=uuid, name=name, object_type="Web API", description=description)
    
    def _parse_report(self, root: ET.Element) -> Optional[SimpleObject]:
        report_elem = root.find('tempoReport')
        if report_elem is None:
            return None
        
        uuid = report_elem.get('{http://www.appian.com/ae/types/2009}uuid')
        name = report_elem.get('name')
        desc_elem = report_elem.find('a:description', self.namespaces)
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        if not uuid or not name:
            return None
        
        return SimpleObject(uuid=uuid, name=name, object_type="Report", description=description)
