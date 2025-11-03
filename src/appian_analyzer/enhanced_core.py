"""
Enhanced Appian Application Analyzer with Object Lookup and Improved XML Parsing
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

@dataclass
class AppianObject:
    """Represents an Appian object with basic metadata"""
    s_no: int
    uuid: str
    name: str
    object_type: str
    description: str
    file_path: str = ""

class EnhancedAppianAnalyzer:
    """Enhanced analyzer with object lookup and detailed XML parsing"""
    
    def __init__(self, zip_path: str):
        self.zip_path = zip_path
        self.zip_file = zipfile.ZipFile(zip_path, 'r')
        self.object_lookup: Dict[str, AppianObject] = {}
        self.namespaces = {
            'a': 'http://www.appian.com/ae/types/2009',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Main analysis method"""
        print("🔍 Starting Enhanced Appian Analysis...")
        
        # Step 1: Create object lookup table
        print("📋 Creating object lookup table...")
        self._create_object_lookup()
        
        # Step 2: Analyze each object type with enhanced parsing
        print("🔧 Analyzing application components...")
        blueprint = {
            "metadata": self._extract_metadata(),
            "object_lookup": {uuid: asdict(obj) for uuid, obj in self.object_lookup.items()},
            "sites": self._analyze_sites(),
            "record_types": self._analyze_record_types(),
            "process_models": self._analyze_process_models(),
            "interfaces": self._analyze_interfaces(),
            "rules": self._analyze_rules(),
            "data_types": self._analyze_data_types(),
            "integrations": self._analyze_integrations(),
            "security_groups": self._analyze_security_groups(),
            "constants": self._analyze_constants(),
            "summary": {}
        }
        
        # Step 3: Generate summary and recommendations
        blueprint["summary"] = self._generate_summary(blueprint)
        
        return blueprint
    
    def _create_object_lookup(self):
        """Create comprehensive object lookup table"""
        s_no = 1
        
        for file_path in self.zip_file.namelist():
            if file_path.endswith('.xml') and not file_path.startswith('META-INF/'):
                try:
                    content = self.zip_file.read(file_path).decode('utf-8')
                    root = ET.fromstring(content)
                    
                    # Extract object info based on file structure
                    uuid, name, description, object_type = self._extract_object_info(root, file_path)
                    
                    if uuid and name:
                        # Skip deprecated objects
                        if "DEPRECATED" not in name.upper():
                            self.object_lookup[uuid] = AppianObject(
                                s_no=s_no,
                                uuid=uuid,
                                name=name,
                                object_type=object_type,
                                description=description,
                                file_path=file_path
                            )
                            s_no += 1
                            
                except Exception as e:
                    print(f"⚠️  Error processing {file_path}: {e}")
                    continue
        
        print(f"📊 Created lookup table with {len(self.object_lookup)} objects")
    
    def _extract_object_info(self, root: ET.Element, file_path: str) -> tuple:
        """Extract object info from different XML structures"""
        uuid = None
        name = None
        description = ""
        object_type = ""
        
        # Determine object type from file path
        if 'recordType/' in file_path:
            object_type = "Record Type"
            record_elem = root.find('recordType')
            if record_elem is not None:
                uuid = record_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = record_elem.get('name')
                desc_elem = record_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'processModel/' in file_path:
            object_type = "Process Model"
            # Process models are nested in process_model_port -> pm -> meta
            pm_port = root.find('{http://www.appian.com/ae/types/2009}process_model_port')
            if pm_port is not None:
                pm_elem = pm_port.find('{http://www.appian.com/ae/types/2009}pm')
                if pm_elem is not None:
                    meta_elem = pm_elem.find('{http://www.appian.com/ae/types/2009}meta')
                    if meta_elem is not None:
                        uuid_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}uuid')
                        name_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}name')
                        desc_elem = meta_elem.find('{http://www.appian.com/ae/types/2009}desc')
                        
                        uuid = uuid_elem.text if uuid_elem is not None and uuid_elem.text else None
                        name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
                        description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                        
                        # If name is empty, use UUID as name
                        if not name and uuid:
                            name = f"Process Model {uuid.split('-')[0]}"
        
        elif 'site/' in file_path:
            object_type = "Site"
            site_elem = root.find('site')
            if site_elem is not None:
                uuid = site_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = site_elem.get('name')
                desc_elem = site_elem.find('description')
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'group/' in file_path:
            object_type = "Security Group"
            group_elem = root.find('group')
            if group_elem is not None:
                uuid_elem = group_elem.find('uuid')
                name_elem = group_elem.find('name')
                desc_elem = group_elem.find('description')
                uuid = uuid_elem.text if uuid_elem is not None and uuid_elem.text else None
                name = name_elem.text if name_elem is not None and name_elem.text else None
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'connectedSystem/' in file_path:
            object_type = "Connected System"
            cs_elem = root.find('connectedSystem')
            if cs_elem is not None:
                uuid = cs_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = cs_elem.get('name')
                desc_elem = cs_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'webApi/' in file_path:
            object_type = "Web API"
            api_elem = root.find('webApi')
            if api_elem is not None:
                uuid = api_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = api_elem.get('name')
                desc_elem = api_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'tempoReport/' in file_path:
            object_type = "Report"
            report_elem = root.find('tempoReport')
            if report_elem is not None:
                uuid = report_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = report_elem.get('name')
                desc_elem = report_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'content/' in file_path:
            # Content can be various types - check the actual element
            for child in root:
                if child.tag.endswith('Haul') or child.tag in ['versionUuid', 'roleMap', 'history', 'migrationVersion']:
                    continue
                
                # Check if it has child elements for metadata (newer format)
                uuid_elem = child.find('uuid')
                name_elem = child.find('name')
                desc_elem = child.find('description')
                
                if uuid_elem is not None and name_elem is not None:
                    uuid = uuid_elem.text
                    name = name_elem.text
                    description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    object_type = self._determine_content_type(child.tag)
                    break
                
                # Fallback to attribute-based extraction (older format)
                uuid_attr = child.get('{http://www.appian.com/ae/types/2009}uuid')
                name_attr = child.get('name')
                if uuid_attr and name_attr:
                    uuid = uuid_attr
                    name = name_attr
                    object_type = self._determine_content_type(child.tag)
                    desc_elem = child.find('a:description', self.namespaces)
                    description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    break
        
        elif 'application/' in file_path:
            object_type = "Application"
            app_elem = root.find('application')
            if app_elem is not None:
                uuid = app_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = app_elem.get('name')
                desc_elem = app_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'dataStore/' in file_path:
            object_type = "Data Store"
            ds_elem = root.find('dataStore')
            if ds_elem is not None:
                uuid = ds_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = ds_elem.get('name')
                desc_elem = ds_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        elif 'Folder' in file_path:
            object_type = "Folder"
            folder_elem = root.find('folder')
            if folder_elem is not None:
                uuid = folder_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                name = folder_elem.get('name')
                desc_elem = folder_elem.find('a:description', self.namespaces)
                description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        return uuid, name, description, object_type
    
    def _determine_content_type(self, tag: str) -> str:
        """Determine content object type from XML tag"""
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
        
        # Remove namespace prefix
        clean_tag = tag.split('}')[-1] if '}' in tag else tag
        return type_mapping.get(clean_tag, clean_tag)
    
    def _analyze_sites(self) -> List[Dict[str, Any]]:
        """Analyze site objects with enhanced parsing"""
        sites = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Site':
                try:
                    content = self.zip_file.read(obj.file_path).decode('utf-8')
                    root = ET.fromstring(content)
                    site_elem = root.find('site', self.namespaces)
                    
                    if site_elem is not None:
                        site_data = {
                            "uuid": uuid,
                            "name": obj.name,
                            "description": obj.description,
                            "pages": self._parse_site_pages(site_elem),
                            "security": self._parse_site_security(root)
                        }
                        sites.append(site_data)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing site {obj.name}: {e}")
        
        return sites
    
    def _parse_site_pages(self, site_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse site pages with hierarchy and UI objects"""
        pages = []
        
        for page_elem in site_elem.findall('page', self.namespaces):
            page_uuid = page_elem.get('{http://www.appian.com/ae/types/2009}uuid')
            static_name = self._get_element_text(page_elem, 'staticName')
            
            page_data = {
                "uuid": page_uuid,
                "name": static_name,
                "ui_objects": [],
                "visibility": self._get_element_text(page_elem, 'visibilityExpr'),
                "sub_pages": []
            }
            
            # Parse UI objects
            ui_elem = page_elem.find('uiObject', self.namespaces)
            if ui_elem is not None:
                ui_uuid = ui_elem.get('{http://www.appian.com/ae/types/2009}uuid')
                ui_type = ui_elem.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
                ui_obj = self.object_lookup.get(ui_uuid)
                page_data["ui_objects"].append({
                    "uuid": ui_uuid,
                    "name": ui_obj.name if ui_obj else "Unknown",
                    "type": ui_type.replace('a:', '') if ui_type else "Unknown"
                })
            
            pages.append(page_data)
        
        return pages
    
    def _analyze_record_types(self) -> List[Dict[str, Any]]:
        """Analyze record types with enhanced field and action parsing"""
        record_types = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Record Type':
                try:
                    content = self.zip_file.read(obj.file_path).decode('utf-8')
                    root = ET.fromstring(content)
                    record_elem = root.find('recordType', self.namespaces)
                    
                    if record_elem is not None:
                        record_data = {
                            "uuid": uuid,
                            "name": obj.name,
                            "description": obj.description,
                            "fields": self._parse_record_fields(record_elem),
                            "relationships": self._parse_record_relationships(record_elem),
                            "actions": self._parse_record_actions(record_elem),
                            "views": self._parse_record_views(record_elem),
                            "security": self._parse_site_security(root)
                        }
                        record_types.append(record_data)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing record type {obj.name}: {e}")
        
        return record_types
    
    def _analyze_process_models(self) -> List[Dict[str, Any]]:
        """Analyze process models with enhanced node parsing"""
        process_models = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Process Model':
                try:
                    content = self.zip_file.read(obj.file_path).decode('utf-8')
                    root = ET.fromstring(content)
                    pm_elem = root.find('processModel')
                    
                    if pm_elem is not None:
                        process_data = {
                            "uuid": uuid,
                            "name": obj.name,
                            "description": obj.description,
                            "variables": self._parse_process_variables(pm_elem),
                            "nodes": self._parse_process_nodes(pm_elem),
                            "flows": self._parse_process_flows(pm_elem),
                            "security": self._parse_pm_security(root)
                        }
                        process_models.append(process_data)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing process model {obj.name}: {e}")
        
        return process_models
    
    def _parse_record_fields(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record type fields"""
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
    
    def _parse_record_relationships(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record type relationships"""
        relationships = []
        
        for rel_elem in record_elem.findall('.//a:recordRelationshipCfg', self.namespaces):
            rel_uuid = self._get_element_text(rel_elem, 'a:uuid')
            target_uuid = self._get_element_text(rel_elem, 'a:targetRecordTypeUuid')
            target_obj = self.object_lookup.get(target_uuid)
            
            rel_data = {
                "uuid": rel_uuid,
                "name": self._get_element_text(rel_elem, 'a:relationshipName'),
                "target_record": {
                    "uuid": target_uuid,
                    "name": target_obj.name if target_obj else "Unknown"
                }
            }
            relationships.append(rel_data)
        
        return relationships
    
    def _parse_record_actions(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record actions with enhanced details"""
        actions = []
        
        for action_elem in record_elem.findall('.//a:relatedActionCfg', self.namespaces):
            action_uuid = action_elem.get('{http://www.appian.com/ae/types/2009}uuid')
            
            # Parse target process model
            target_elem = action_elem.find('a:target', self.namespaces)
            target_uuid = target_elem.get('{http://www.appian.com/ae/types/2009}uuid') if target_elem is not None else None
            target_obj = self.object_lookup.get(target_uuid) if target_uuid else None
            
            action_data = {
                "uuid": action_uuid,
                "title": self._get_text_or_expression(action_elem.find('a:titleExpr', self.namespaces)),
                "description": self._get_text_or_expression(action_elem.find('a:descriptionExpr', self.namespaces)),
                "target_process": {
                    "uuid": target_uuid,
                    "name": target_obj.name if target_obj else "Unknown"
                },
                "context": self._get_element_text(action_elem, 'a:contextExpr'),
                "visibility": self._get_element_text(action_elem, 'a:visibilityExpr'),
                "security": self._parse_action_security(action_elem)
            }
            actions.append(action_data)
        
        return actions
    
    def _parse_record_views(self, record_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse record views"""
        views = []
        
        for view_elem in record_elem.findall('.//a:recordView', self.namespaces):
            view_data = {
                "name": self._get_element_text(view_elem, 'a:name'),
                "type": self._get_element_text(view_elem, 'a:type')
            }
            views.append(view_data)
        
        return views
    
    def _parse_process_variables(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
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
    
    def _parse_process_nodes(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
        """Parse process model nodes with detailed analysis"""
        nodes = []
        
        for node_elem in pm_elem.findall('.//nodes/node'):
            node_uuid = node_elem.get('uuid')
            node_data = {
                "uuid": node_uuid,
                "name": self._get_element_text(node_elem, 'name'),
                "type": self._determine_node_type(node_elem),
                "details": self._parse_node_details(node_elem)
            }
            nodes.append(node_data)
        
        return nodes
    
    def _parse_process_flows(self, pm_elem: ET.Element) -> List[Dict[str, Any]]:
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
    
    def _parse_site_security(self, root: ET.Element) -> Dict[str, Any]:
        """Parse site security configuration"""
        return self._parse_security_from_rolemap(root)
    
    def _parse_pm_security(self, root: ET.Element) -> Dict[str, Any]:
        """Parse process model security configuration"""
        security = {"roles": []}
        
        role_map = root.find('roleMap')
        if role_map is not None:
            for role_elem in role_map.findall('role'):
                role_name = role_elem.get('name')
                
                # Get users
                users_elem = role_elem.find('users')
                users = []
                if users_elem is not None:
                    for user_elem in users_elem.findall('userUuid'):
                        users.append(user_elem.text)
                
                # Get groups
                groups_elem = role_elem.find('groups')
                groups = []
                if groups_elem is not None:
                    for group_elem in groups_elem.findall('groupUuid'):
                        group_uuid = group_elem.text
                        group_obj = self.object_lookup.get(group_uuid)
                        groups.append({
                            "uuid": group_uuid,
                            "name": group_obj.name if group_obj else "Unknown"
                        })
                
                if users or groups:
                    security["roles"].append({
                        "role": role_name,
                        "users": users,
                        "groups": groups
                    })
        
        return security
    
    def _parse_security_from_rolemap(self, root: ET.Element) -> Dict[str, Any]:
        """Parse security from roleMap structure"""
        security = {"roles": []}
        
        for role_elem in root.findall('.//roleMap/role'):
            role_name = role_elem.get('name')
            
            # Get users and groups
            users = [u.text for u in role_elem.findall('.//userUuid')]
            group_uuids = [g.text for g in role_elem.findall('.//groupUuid')]
            
            groups = []
            for group_uuid in group_uuids:
                group_obj = self.object_lookup.get(group_uuid)
                groups.append({
                    "uuid": group_uuid,
                    "name": group_obj.name if group_obj else "Unknown"
                })
            
            if users or groups:
                security["roles"].append({
                    "role": role_name,
                    "users": users,
                    "groups": groups
                })
        
        return security
    
    def _analyze_interfaces(self) -> List[Dict[str, Any]]:
        """Analyze interfaces"""
        interfaces = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Interface':
                interfaces.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description
                })
        
        return interfaces
    
    def _analyze_rules(self) -> List[Dict[str, Any]]:
        """Analyze expression rules"""
        rules = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Expression Rule':
                rules.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description
                })
        
        return rules
    
    def _analyze_data_types(self) -> List[Dict[str, Any]]:
        """Analyze data types (CDTs)"""
        data_types = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Data Type':
                data_types.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description
                })
        
        return data_types
    
    def _analyze_integrations(self) -> List[Dict[str, Any]]:
        """Analyze integrations and connected systems"""
        integrations = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type in ['Connected System', 'Web API']:
                integrations.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description,
                    "type": obj.object_type
                })
        
        return integrations
    
    def _analyze_security_groups(self) -> List[Dict[str, Any]]:
        """Analyze security groups"""
        groups = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Security Group':
                groups.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description,
                    "type": self._classify_group_type(obj.name)
                })
        
        return groups
    
    def _analyze_constants(self) -> List[Dict[str, Any]]:
        """Analyze constants"""
        constants = []
        
        for uuid, obj in self.object_lookup.items():
            if obj.object_type == 'Constant':
                constants.append({
                    "uuid": uuid,
                    "name": obj.name,
                    "description": obj.description
                })
        
        return constants
    
    def _determine_node_type(self, node_elem: ET.Element) -> str:
        """Determine the type of process node"""
        # Check for form configuration
        if node_elem.find('.//form-config') is not None:
            return "User Input Task"
        
        # Check for expression
        if node_elem.find('.//expr') is not None:
            return "Script Task"
        
        # Check for subprocess call
        if node_elem.find('.//subprocess') is not None:
            return "Call Process"
        
        return "Unknown"
    
    def _parse_node_details(self, node_elem: ET.Element) -> Dict[str, Any]:
        """Parse detailed node configuration"""
        details = {}
        
        # Parse form configuration
        form_config = node_elem.find('.//form-config')
        if form_config is not None:
            ui_expr = form_config.find('.//uiExpressionForm')
            if ui_expr is not None:
                interface_uuid = ui_expr.text
                interface_obj = self.object_lookup.get(interface_uuid)
                details["interface"] = {
                    "uuid": interface_uuid,
                    "name": interface_obj.name if interface_obj else "Unknown"
                }
        
        # Parse expressions
        expr_elem = node_elem.find('.//expr')
        if expr_elem is not None:
            details["expression"] = expr_elem.text
        
        return details
    
    def _parse_security(self, root: ET.Element) -> Dict[str, Any]:
        """Parse security configuration - simplified"""
        return {"roles": []}
    
    def _parse_action_security(self, action_elem: ET.Element) -> Dict[str, Any]:
        """Parse action-specific security"""
        return {}
    
    def _parse_rule_inputs(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse rule inputs - simplified"""
        return []
    
    def _parse_data_type_elements(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse data type elements - simplified"""
        return []
    
    def _classify_group_type(self, group_name: str) -> str:
        """Classify security group type based on name patterns"""
        name_lower = group_name.lower()
        
        if any(word in name_lower for word in ['admin', 'administrator']):
            return 'Administrative'
        elif any(word in name_lower for word in ['read', 'view', 'viewer']):
            return 'Read-Only'
        elif any(word in name_lower for word in ['edit', 'editor', 'modify']):
            return 'Editor'
        elif any(word in name_lower for word in ['user', 'basic']):
            return 'Basic User'
        else:
            return 'Functional'
    
    def _get_element_text(self, parent: ET.Element, xpath: str) -> str:
        """Safely get element text"""
        elem = parent.find(xpath, self.namespaces)
        return elem.text if elem is not None and elem.text else ""
    
    def _get_text_or_expression(self, elem: ET.Element) -> str:
        """Get text or parse expression reference"""
        if elem is None or not elem.text:
            return ""
        
        text = elem.text.strip()
        
        # Check if it's an expression rule reference
        if text.startswith('#"_a-') and text.endswith('"()'):
            # Extract UUID from expression
            uuid_match = re.search(r'_a-([a-f0-9-]+)', text)
            if uuid_match:
                full_uuid = f"_a-{uuid_match.group(1)}"
                obj = self.object_lookup.get(full_uuid)
                return f"Expression: {obj.name}" if obj else f"Expression: {full_uuid}"
        
        return text
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract application metadata"""
        app_name = os.path.basename(self.zip_path).replace('.zip', '')
        
        return {
            "application_name": app_name,
            "total_objects": len(self.object_lookup),
            "analysis_timestamp": "2025-11-03T12:06:39.395+05:30"
        }
    
    def _generate_summary(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""
        return {
            "total_sites": len(blueprint["sites"]),
            "total_record_types": len(blueprint["record_types"]),
            "total_process_models": len(blueprint["process_models"]),
            "total_interfaces": len(blueprint["interfaces"]),
            "total_rules": len(blueprint["rules"]),
            "total_data_types": len(blueprint["data_types"]),
            "total_integrations": len(blueprint["integrations"]),
            "total_security_groups": len(blueprint["security_groups"]),
            "total_constants": len(blueprint["constants"]),
            "complexity_assessment": self._assess_complexity(blueprint),
            "recommendations": self._generate_recommendations(blueprint)
        }
    
    def _assess_complexity(self, blueprint: Dict[str, Any]) -> str:
        """Assess application complexity"""
        total_objects = len(self.object_lookup)
        
        if total_objects > 400:
            return "Very High"
        elif total_objects > 200:
            return "High"
        elif total_objects > 100:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, blueprint: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if len(blueprint["record_types"]) > 50:
            recommendations.append("Consider data model consolidation - high number of record types detected")
        
        if len(blueprint["integrations"]) > 10:
            recommendations.append("Implement integration governance framework for better management")
        
        if len(blueprint["security_groups"]) > 100:
            recommendations.append("Review security group structure for consolidation opportunities")
        
        return recommendations
    
    def close(self):
        """Close the zip file"""
        self.zip_file.close()
