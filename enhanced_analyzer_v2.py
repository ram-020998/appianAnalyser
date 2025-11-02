#!/usr/bin/env python3
"""
Enhanced Appian Analyzer v2 - Following TO DO NOW requirements
"""

import zipfile
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
import xml.etree.ElementTree as ET
import urllib.parse
import re

class EnhancedAppianAnalyzer:
    """Enhanced analyzer with JSON object lookup and detailed extraction"""
    
    def __init__(self, zip_path: str):
        self.zip_path = Path(zip_path)
        self.extract_dir = Path("temp_extract")
        self.output_dir = Path("output")
        self.object_lookup = {}
        self.blueprint = {}
        
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")
        
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self):
        """Enhanced analysis following TO DO NOW requirements"""
        print(f"🚀 Enhanced Analysis: {self.zip_path.name}")
        
        try:
            self._clean_output_folder()
            self._extract_application()
            self._create_object_lookup()
            self._analyze_components()
            self._generate_outputs()
            self._invoke_q_agent()
            
            print("✅ Enhanced analysis complete!")
            
        finally:
            self._cleanup()
    
    def _extract_application(self):
        """Extract zip file"""
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
        self.extract_dir.mkdir(parents=True)
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)
        print(f"📦 Extracted to {self.extract_dir}")
    
    def _create_object_lookup(self):
        """Create JSON object lookup table"""
        print("📋 Creating JSON object lookup table...")
        
        lookup_objects = []
        s_no = 1
        
        # Process all XML files to build lookup
        for xml_file in self.extract_dir.rglob("*.xml"):
            if "META-INF" in str(xml_file):
                continue
            
            obj_info = self._extract_object_basic_info(xml_file)
            if obj_info:
                obj_info["s_no"] = s_no
                lookup_objects.append(obj_info)
                self.object_lookup[obj_info["uuid"]] = obj_info
                s_no += 1
        
        # Save as JSON
        lookup_file = self.output_dir / f"{self.zip_path.stem}_object_lookup.json"
        with open(lookup_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_objects": len(lookup_objects),
                "objects": lookup_objects
            }, f, indent=2)
        
        print(f"📊 JSON lookup table: {lookup_file}")
        print(f"📊 Created lookup with {len(lookup_objects)} objects")
    
    def _extract_object_basic_info(self, xml_file: Path) -> Optional[Dict]:
        """Extract basic object information"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Determine object type from path
            object_type = self._get_object_type_from_path(xml_file)
            
            # Extract based on type
            if object_type == "Site":
                site_elem = root.find(".//site")
                if site_elem is not None:
                    return {
                        "uuid": site_elem.get("uuid", xml_file.stem),
                        "name": site_elem.get("name", "Unnamed Site"),
                        "type": object_type,
                        "description": self._safe_get_text(root, ".//description"),
                        "file": xml_file.name
                    }
            
            elif object_type == "Record Type":
                record_elem = root.find(".//recordType")
                if record_elem is not None:
                    uuid = record_elem.get("{http://www.appian.com/ae/types/2009}uuid") or record_elem.get("uuid") or xml_file.stem
                    name = record_elem.get("name", "Unnamed Record")
                    return {
                        "uuid": uuid,
                        "name": name,
                        "type": object_type,
                        "description": self._safe_get_text(record_elem, "{http://www.appian.com/ae/types/2009}description"),
                        "file": xml_file.name
                    }
            
            elif object_type == "Process Model":
                name = self._safe_get_text(root, ".//name")
                uuid = self._safe_get_text(root, ".//uuid") or xml_file.stem
                return {
                    "uuid": uuid,
                    "name": name or "Unnamed Process",
                    "type": object_type,
                    "description": self._safe_get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
            elif object_type == "CDT":
                # For CDTs, extract from XSD
                complex_types = root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
                if complex_types:
                    ct = complex_types[0]
                    name = ct.get("name", "Unnamed CDT")
                    return {
                        "uuid": xml_file.stem,
                        "name": name,
                        "type": object_type,
                        "description": self._extract_table_name_from_cdt(ct),
                        "file": xml_file.name
                    }
            
            elif object_type == "Security Group":
                name = self._safe_get_text(root, ".//name")
                uuid = self._safe_get_text(root, ".//uuid") or xml_file.stem
                return {
                    "uuid": uuid,
                    "name": name or "Unnamed Group",
                    "type": object_type,
                    "description": self._safe_get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
            elif object_type == "Connected System":
                name = self._safe_get_text(root, ".//name")
                uuid = self._safe_get_text(root, ".//uuid") or xml_file.stem
                return {
                    "uuid": uuid,
                    "name": name or "Unnamed System",
                    "type": object_type,
                    "description": self._safe_get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
            elif object_type == "Web API":
                name = self._safe_get_text(root, ".//name")
                uuid = self._safe_get_text(root, ".//uuid") or xml_file.stem
                return {
                    "uuid": uuid,
                    "name": name or "Unnamed API",
                    "type": object_type,
                    "description": self._safe_get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
        except ET.ParseError:
            pass
        
        return None
    
    def _get_object_type_from_path(self, xml_file: Path) -> str:
        """Get object type from file path"""
        path_str = str(xml_file)
        
        if "/site/" in path_str:
            return "Site"
        elif "/recordType/" in path_str:
            return "Record Type"
        elif "/processModel/" in path_str:
            return "Process Model"
        elif "/datatype/" in path_str:
            return "CDT"
        elif "/group/" in path_str:
            return "Security Group"
        elif "/connectedSystem/" in path_str:
            return "Connected System"
        elif "/webApi/" in path_str:
            return "Web API"
        elif "/content/" in path_str:
            return "Interface/Content"
        else:
            return "Unknown"
    
    def _safe_get_text(self, element: ET.Element, xpath: str) -> str:
        """Safely get text from element"""
        try:
            found = element.find(xpath)
            return found.text.strip() if found is not None and found.text else ""
        except Exception:
            return ""
    
    def _extract_table_name_from_cdt(self, complex_type: ET.Element) -> str:
        """Extract table name from CDT"""
        try:
            annotations = complex_type.findall(".//annotation")
            for annotation in annotations:
                appinfo = annotation.find(".//appinfo")
                if appinfo is not None and appinfo.text and "@Table(name=" in appinfo.text:
                    text = appinfo.text
                    start = text.find('name="') + 6
                    end = text.find('"', start)
                    if start > 5 and end > start:
                        return f"Table: {text[start:end]}"
        except Exception:
            pass
        return ""
    
    def _analyze_components(self):
        """Analyze all components with enhanced extraction"""
        print("🔍 Analyzing components...")
        
        self.blueprint = {
            "application_info": self._get_application_info(),
            "sites": self._analyze_sites(),
            "record_types": self._analyze_record_types(),
            "process_models": self._analyze_process_models(),
            "data_types": self._analyze_data_types(),
            "integrations": self._analyze_integrations(),
            "security_groups": self._analyze_security_groups(),
            "summary": self._generate_summary()
        }
    
    def _get_application_info(self) -> Dict:
        """Get application information"""
        app_dir = self.extract_dir / "application"
        if not app_dir.exists():
            return {"name": "Unknown Application"}
        
        for xml_file in app_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                app_elem = root.find(".//application")
                if app_elem is not None:
                    return {
                        "name": app_elem.get("name", "Unknown"),
                        "description": self._safe_get_text(app_elem, "description"),
                        "uuid": app_elem.get("uuid", "")
                    }
            except ET.ParseError:
                continue
        
        return {"name": "Unknown Application"}
    
    def _analyze_sites(self) -> List[Dict]:
        """Analyze sites with enhanced extraction"""
        sites = []
        site_dir = self.extract_dir / "site"
        
        if not site_dir.exists():
            return sites
        
        for xml_file in site_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                site_elem = root.find(".//site")
                if site_elem is not None:
                    site_info = {
                        "name": site_elem.get("name", ""),
                        "uuid": site_elem.get("uuid", ""),
                        "description": self._safe_get_text(site_elem, "description"),
                        "pages": self._extract_site_pages(site_elem)
                    }
                    sites.append(site_info)
            except ET.ParseError:
                continue
        
        return sites
    
    def _extract_site_pages(self, site_elem: ET.Element) -> List[Dict]:
        """Extract site pages with UI objects and visibility"""
        pages = []
        
        for page_elem in site_elem.findall(".//page"):
            # Extract UI object
            ui_object_elem = page_elem.find(".//uiObject")
            ui_object_uuid = ui_object_elem.get("uuid") if ui_object_elem is not None else ""
            
            # Extract visibility expression
            visibility_expr = self._safe_get_text(page_elem, "visibilityExpr")
            
            page_info = {
                "uuid": page_elem.get("uuid", ""),
                "name": self._safe_get_text(page_elem, "nameExpr"),
                "url_stub": self._safe_get_text(page_elem, "urlStub"),
                "ui_object": {
                    "uuid": ui_object_uuid,
                    "name": self._resolve_name(ui_object_uuid)
                },
                "visibility": {
                    "expression": visibility_expr,
                    "expression_rules": self._extract_expression_uuids(visibility_expr)
                }
            }
            pages.append(page_info)
        
        return pages
    
    def _resolve_name(self, uuid: str) -> str:
        """Resolve object name from UUID"""
        if not uuid:
            return ""
        if uuid in self.object_lookup:
            return self.object_lookup[uuid]["name"]
        return f"Unknown ({uuid[:8]}...)"
    
    def _extract_expression_uuids(self, expression: str) -> List[Dict]:
        """Extract expression rule UUIDs from expressions"""
        if not expression:
            return []
        
        # Pattern for expression rules: #"uuid"()
        pattern = r'#"([a-f0-9-_]+)"'
        matches = re.findall(pattern, expression)
        
        rules = []
        for uuid in matches:
            rules.append({
                "uuid": uuid,
                "name": self._resolve_name(uuid)
            })
        
        return rules
    
    def _analyze_record_types(self) -> List[Dict]:
        """Analyze record types with actions and relationships"""
        record_types = []
        rt_dir = self.extract_dir / "recordType"
        
        if not rt_dir.exists():
            return record_types
        
        for xml_file in rt_dir.glob("*.xml"):
            if "deprecated" in xml_file.name.lower():
                continue
                
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                record_elem = root.find(".//recordType")
                if record_elem is not None:
                    rt_info = {
                        "name": record_elem.get("name", ""),
                        "uuid": record_elem.get("{http://www.appian.com/ae/types/2009}uuid", ""),
                        "description": self._safe_get_text(record_elem, "{http://www.appian.com/ae/types/2009}description"),
                        "actions": self._extract_record_actions(root),
                        "relationships": self._extract_record_relationships(root),
                        "fields": self._extract_record_fields(root)
                    }
                    record_types.append(rt_info)
            except ET.ParseError:
                continue
        
        return record_types
    
    def _extract_record_actions(self, root: ET.Element) -> List[Dict]:
        """Extract record actions with detailed information"""
        actions = []
        
        # Extract related actions
        for action_elem in root.findall(".//{http://www.appian.com/ae/types/2009}relatedActionCfg"):
            target_elem = action_elem.find(".//{http://www.appian.com/ae/types/2009}target")
            
            if target_elem is not None:
                target_uuid = target_elem.get("{http://www.appian.com/ae/types/2009}uuid", "")
                target_type = target_elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
                
                action_info = {
                    "uuid": action_elem.get("{http://www.appian.com/ae/types/2009}uuid", ""),
                    "title": self._safe_get_text(action_elem, "{http://www.appian.com/ae/types/2009}titleExpr"),
                    "description": self._safe_get_text(action_elem, "{http://www.appian.com/ae/types/2009}descriptionExpr"),
                    "reference_key": self._safe_get_text(action_elem, "{http://www.appian.com/ae/types/2009}referenceKey"),
                    "target": {
                        "uuid": target_uuid,
                        "name": self._resolve_name(target_uuid),
                        "type": target_type
                    },
                    "context": self._safe_get_text(action_elem, "{http://www.appian.com/ae/types/2009}contextExpr"),
                    "visibility": self._safe_get_text(action_elem, "{http://www.appian.com/ae/types/2009}visibilityExpr")
                }
                actions.append(action_info)
        
        return actions
    
    def _extract_record_relationships(self, root: ET.Element) -> List[Dict]:
        """Extract record relationships"""
        relationships = []
        
        for rel_elem in root.findall(".//{http://www.appian.com/ae/types/2009}recordRelationshipCfg"):
            target_uuid = self._safe_get_text(rel_elem, "targetRecordTypeUuid")
            
            rel_info = {
                "uuid": self._safe_get_text(rel_elem, "uuid"),
                "name": self._safe_get_text(rel_elem, "relationshipName"),
                "target_record": {
                    "uuid": target_uuid,
                    "name": self._resolve_name(target_uuid)
                },
                "type": self._safe_get_text(rel_elem, "relationshipType"),
                "update_behavior": self._safe_get_text(rel_elem, "updateBehavior")
            }
            relationships.append(rel_info)
        
        return relationships
    
    def _extract_record_fields(self, root: ET.Element) -> List[Dict]:
        """Extract record fields"""
        fields = []
        
        for field_elem in root.findall(".//field"):
            field_info = {
                "uuid": self._safe_get_text(field_elem, "uuid"),
                "name": self._safe_get_text(field_elem, "fieldName"),
                "type": self._safe_get_text(field_elem, "type"),
                "source_field": self._safe_get_text(field_elem, "sourceFieldName"),
                "is_record_id": self._safe_get_text(field_elem, "isRecordId") == "true",
                "is_custom": self._safe_get_text(field_elem, "isCustomField") == "true"
            }
            if field_info["name"]:
                fields.append(field_info)
        
        return fields
    
    def _analyze_process_models(self) -> List[Dict]:
        """Analyze process models"""
        process_models = []
        pm_dir = self.extract_dir / "processModel"
        
        if not pm_dir.exists():
            return process_models
        
        for xml_file in pm_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                name = self._safe_get_text(root, ".//name")
                if name:
                    pm_info = {
                        "name": name,
                        "uuid": self._safe_get_text(root, ".//uuid"),
                        "description": self._safe_get_text(root, ".//description"),
                        "nodes": self._extract_process_nodes(root)
                    }
                    process_models.append(pm_info)
            except ET.ParseError:
                continue
        
        return process_models
    
    def _extract_process_nodes(self, root: ET.Element) -> List[Dict]:
        """Extract process nodes with business logic"""
        nodes = []
        
        for node_elem in root.findall(".//node"):
            node_info = {
                "uuid": node_elem.get("uuid", ""),
                "type": node_elem.get("type", ""),
                "name": self._safe_get_text(node_elem, "name"),
                "description": self._safe_get_text(node_elem, "description")
            }
            nodes.append(node_info)
        
        return nodes
    
    def _analyze_data_types(self) -> List[Dict]:
        """Analyze CDTs"""
        data_types = []
        dt_dir = self.extract_dir / "datatype"
        
        if not dt_dir.exists():
            return data_types
        
        for xsd_file in dt_dir.glob("*.xsd"):
            if "deprecated" in xsd_file.name.lower():
                continue
                
            try:
                tree = ET.parse(xsd_file)
                root = tree.getroot()
                
                complex_types = root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
                for ct in complex_types:
                    name = ct.get("name")
                    if name:
                        dt_info = {
                            "name": name,
                            "table_name": self._extract_table_name_from_cdt(ct),
                            "fields": self._extract_cdt_fields(ct),
                            "relationships": self._extract_cdt_relationships(root)
                        }
                        data_types.append(dt_info)
            except ET.ParseError:
                continue
        
        return data_types
    
    def _extract_cdt_fields(self, complex_type: ET.Element) -> List[Dict]:
        """Extract CDT fields"""
        fields = []
        
        try:
            sequences = complex_type.findall(".//sequence")
            for seq in sequences:
                elements = seq.findall(".//element")
                for elem in elements:
                    field_info = {
                        "name": elem.get("name", ""),
                        "type": elem.get("type", ""),
                        "nullable": elem.get("nillable") == "true",
                        "column_name": self._extract_column_name(elem)
                    }
                    if field_info["name"]:
                        fields.append(field_info)
        except Exception:
            pass
        
        return fields
    
    def _extract_column_name(self, element: ET.Element) -> str:
        """Extract database column name from element"""
        try:
            annotations = element.findall(".//annotation")
            for annotation in annotations:
                appinfo = annotation.find(".//appinfo")
                if appinfo is not None and appinfo.text and "@Column(name=" in appinfo.text:
                    text = appinfo.text
                    start = text.find('name="') + 6
                    end = text.find('"', start)
                    if start > 5 and end > start:
                        return text[start:end]
        except Exception:
            pass
        return ""
    
    def _extract_cdt_relationships(self, root: ET.Element) -> List[str]:
        """Extract CDT relationships from includes"""
        relationships = []
        
        try:
            includes = root.findall(".//{http://www.w3.org/2001/XMLSchema}include")
            for include in includes:
                schema_location = include.get("schemaLocation", "")
                if schema_location:
                    # Decode the schema location to get related CDT name
                    decoded = urllib.parse.unquote(schema_location)
                    if "}" in decoded:
                        cdt_name = decoded.split("}")[-1].replace(".xsd", "")
                        relationships.append(cdt_name)
        except Exception:
            pass
        
        return relationships
    
    def _analyze_integrations(self) -> List[Dict]:
        """Analyze integrations"""
        integrations = []
        
        # Connected Systems
        cs_dir = self.extract_dir / "connectedSystem"
        if cs_dir.exists():
            for xml_file in cs_dir.glob("*.xml"):
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    name = self._safe_get_text(root, ".//name")
                    if name:
                        integrations.append({
                            "name": name,
                            "type": "Connected System",
                            "system_type": self._safe_get_text(root, ".//type")
                        })
                except ET.ParseError:
                    continue
        
        # Web APIs
        api_dir = self.extract_dir / "webApi"
        if api_dir.exists():
            for xml_file in api_dir.glob("*.xml"):
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    name = self._safe_get_text(root, ".//name")
                    if name:
                        integrations.append({
                            "name": name,
                            "type": "Web API"
                        })
                except ET.ParseError:
                    continue
        
        return integrations
    
    def _analyze_security_groups(self) -> List[Dict]:
        """Analyze security groups"""
        groups = []
        group_dir = self.extract_dir / "group"
        
        if not group_dir.exists():
            return groups
        
        for xml_file in group_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                name = self._safe_get_text(root, ".//name")
                if name:
                    groups.append({
                        "name": name,
                        "uuid": self._safe_get_text(root, ".//uuid"),
                        "description": self._safe_get_text(root, ".//description")
                    })
            except ET.ParseError:
                continue
        
        return groups
    
    def _generate_summary(self) -> Dict:
        """Generate analysis summary"""
        return {
            "total_objects": len(self.object_lookup),
            "sites_count": len(self.blueprint.get("sites", [])),
            "record_types_count": len(self.blueprint.get("record_types", [])),
            "process_models_count": len(self.blueprint.get("process_models", [])),
            "data_types_count": len(self.blueprint.get("data_types", [])),
            "integrations_count": len(self.blueprint.get("integrations", [])),
            "security_groups_count": len(self.blueprint.get("security_groups", [])),
            "actions_count": sum(len(rt.get("actions", [])) for rt in self.blueprint.get("record_types", []))
        }
    
    def _generate_outputs(self):
        """Generate all output files"""
        # Save enhanced blueprint
        blueprint_file = self.output_dir / f"{self.zip_path.stem}_enhanced_blueprint.json"
        with open(blueprint_file, 'w') as f:
            json.dump(self.blueprint, f, indent=2)
        print(f"💾 Enhanced blueprint: {blueprint_file}")
        
        # Print summary
        summary = self.blueprint["summary"]
        print(f"\n📊 Analysis Summary:")
        print(f"  📱 Application: {self.blueprint['application_info']['name']}")
        print(f"  🏠 Sites: {summary['sites_count']}")
        print(f"  📋 Record Types: {summary['record_types_count']}")
        print(f"  ⚡ Actions: {summary['actions_count']}")
        print(f"  ⚙️  Process Models: {summary['process_models_count']}")
        print(f"  📊 Data Types: {summary['data_types_count']}")
        print(f"  🔗 Integrations: {summary['integrations_count']}")
        print(f"  🔒 Security Groups: {summary['security_groups_count']}")
    
    def _clean_output_folder(self):
        """Clean old files from output folder"""
        if self.output_dir.exists():
            for file in self.output_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            print("🧹 Cleaned output folder")
        else:
            self.output_dir.mkdir(exist_ok=True)
    
    def _invoke_q_agent(self):
        """Invoke Amazon Q agent to generate readable blueprint"""
        try:
            from pathlib import Path
            import sys
            
            # Add .amazonq to path
            amazonq_path = Path(__file__).parent / ".amazonq"
            sys.path.insert(0, str(amazonq_path))
            
            from blueprint_agent import AmazonQBlueprintAgent
            
            blueprint_file = self.output_dir / f"{self.zip_path.stem}_enhanced_blueprint.json"
            lookup_file = self.output_dir / f"{self.zip_path.stem}_object_lookup.json"
            
            print("\n🤖 Invoking Amazon Q agent for readable blueprint...")
            agent = AmazonQBlueprintAgent(str(blueprint_file), str(lookup_file))
            readable_file = agent.generate_readable_blueprint()
            
            print(f"📖 Human-readable blueprint: {readable_file}")
            
        except Exception as e:
            print(f"⚠️  Could not invoke Q agent: {e}")
            print("💡 You can manually run: python3 .amazonq/blueprint_agent.py <blueprint> <lookup>")
    
    def _cleanup(self):
        """Clean up extracted files"""
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)

def main():
    """Test the enhanced analyzer"""
    zip_path = "applicationZips/RequirementsManagementv2.3.0.zip"
    
    if not Path(zip_path).exists():
        print(f"❌ Zip file not found: {zip_path}")
        return
    
    analyzer = EnhancedAppianAnalyzer(zip_path)
    analyzer.analyze()

if __name__ == "__main__":
    main()
