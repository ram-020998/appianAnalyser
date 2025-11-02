import zipfile
import shutil
import json
import csv
from pathlib import Path
from typing import Optional, Dict, List, Any
import xml.etree.ElementTree as ET
import urllib.parse
import re

class EnhancedAppianAnalyzer:
    """Enhanced Appian analyzer with object lookup and detailed extraction"""
    
    def __init__(self, zip_path: str, extract_dir: str = "temp_extract", output_dir: str = "output"):
        self.zip_path = Path(zip_path)
        self.extract_dir = Path(extract_dir)
        self.output_dir = Path(output_dir)
        self.object_lookup = {}  # UUID -> object info
        self.expression_rules = {}  # UUID -> expression rule info
        self.blueprint = {}
        
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")
        
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self) -> Dict[str, Any]:
        """Enhanced analysis with object lookup"""
        print(f"🔍 Enhanced Analysis: {self.zip_path.name}")
        
        try:
            self._extract_application()
            self._create_object_lookup()
            self._analyze_all_components()
            self._generate_human_readable_blueprint()
            
            print("✅ Enhanced analysis complete!")
            return self.blueprint
            
        finally:
            self._cleanup()
    
    def _extract_application(self):
        """Extract the Appian zip file"""
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
        self.extract_dir.mkdir(parents=True)
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)
        print(f"📦 Extracted to {self.extract_dir}")
    
    def _create_object_lookup(self):
        """Create comprehensive object lookup table"""
        print("📋 Creating object lookup table...")
        
        lookup_data = []
        s_no = 1
        
        # Process all XML files to build lookup
        for xml_file in self.extract_dir.rglob("*.xml"):
            if "META-INF" in str(xml_file):
                continue
                
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Determine object type from directory
                object_type = self._get_object_type(xml_file)
                
                # Extract object info
                obj_info = self._extract_object_info(root, object_type, xml_file)
                if obj_info:
                    obj_info["s_no"] = s_no
                    lookup_data.append(obj_info)
                    self.object_lookup[obj_info["uuid"]] = obj_info
                    s_no += 1
                    
            except ET.ParseError:
                continue
        
        # Save lookup table
        self._save_lookup_table(lookup_data)
        print(f"📊 Created lookup table with {len(lookup_data)} objects")
    
    def _get_object_type(self, xml_file: Path) -> str:
        """Determine object type from file path"""
        path_parts = xml_file.parts
        
        if "site" in path_parts:
            return "Site"
        elif "datatype" in path_parts:
            return "CDT"
        elif "recordType" in path_parts:
            return "Record Type"
        elif "processModel" in path_parts:
            return "Process Model"
        elif "connectedSystem" in path_parts:
            return "Connected System"
        elif "webApi" in path_parts:
            return "Web API"
        elif "group" in path_parts:
            return "Security Group"
        elif "content" in path_parts:
            return "Interface/Content"
        else:
            return "Unknown"
    
    def _extract_object_info(self, root: ET.Element, object_type: str, xml_file: Path) -> Optional[Dict]:
        """Extract basic object information"""
        try:
            if object_type == "Site":
                site_elem = root.find(".//site")
                if site_elem is not None:
                    return {
                        "uuid": site_elem.get("uuid", ""),
                        "name": site_elem.get("name", ""),
                        "type": object_type,
                        "description": self._get_text(root, ".//description"),
                        "file": xml_file.name
                    }
            
            elif object_type == "CDT":
                # Extract from XSD schema
                complex_types = root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
                if complex_types:
                    ct = complex_types[0]  # Take first complex type
                    return {
                        "uuid": xml_file.stem,  # Use filename as UUID for CDTs
                        "name": ct.get("name", ""),
                        "type": object_type,
                        "description": self._extract_table_name_from_cdt(ct),
                        "file": xml_file.name
                    }
            
            elif object_type == "Record Type":
                record_elem = root.find(".//recordType")
                if record_elem is not None:
                    return {
                        "uuid": record_elem.get("{http://www.appian.com/ae/types/2009}uuid", ""),
                        "name": record_elem.get("name", ""),
                        "type": object_type,
                        "description": self._get_text(record_elem, "{http://www.appian.com/ae/types/2009}description"),
                        "file": xml_file.name
                    }
            
            elif object_type == "Process Model":
                return {
                    "uuid": self._get_text(root, ".//uuid"),
                    "name": self._get_text(root, ".//name"),
                    "type": object_type,
                    "description": self._get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
            elif object_type == "Security Group":
                return {
                    "uuid": self._get_text(root, ".//uuid"),
                    "name": self._get_text(root, ".//name"),
                    "type": object_type,
                    "description": self._get_text(root, ".//description"),
                    "file": xml_file.name
                }
            
            # Add other object types as needed
            
        except Exception:
            pass
        
        return None
    
    def _extract_table_name_from_cdt(self, complex_type: ET.Element) -> str:
        """Extract table name from CDT annotations"""
        try:
            annotations = complex_type.findall(".//annotation")
            for annotation in annotations:
                appinfo = annotation.find(".//appinfo")
                if appinfo is not None and appinfo.text:
                    text = appinfo.text
                    if "@Table(name=" in text:
                        start = text.find('name="') + 6
                        end = text.find('"', start)
                        return f"Table: {text[start:end]}" if start > 5 and end > start else ""
        except Exception:
            pass
        return ""
    
    def _get_text(self, element: ET.Element, xpath: str) -> str:
        """Safely extract text from XML element"""
        try:
            found = element.find(xpath)
            return found.text.strip() if found is not None and found.text else ""
        except Exception:
            return ""
    
    def _save_lookup_table(self, lookup_data: List[Dict]):
        """Save object lookup table as CSV"""
        csv_file = self.output_dir / f"{self.zip_path.stem}_object_lookup.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if lookup_data:
                writer = csv.DictWriter(f, fieldnames=["s_no", "uuid", "name", "type", "description", "file"])
                writer.writeheader()
                writer.writerows(lookup_data)
        
        print(f"📊 Object lookup saved to {csv_file}")
    
    def _analyze_all_components(self):
        """Analyze all components with enhanced extraction"""
        self.blueprint = {
            "application_info": self._analyze_application_info(),
            "sites": self._analyze_sites_enhanced(),
            "data_model": self._analyze_data_model_enhanced(),
            "record_types": self._analyze_record_types_enhanced(),
            "process_models": self._analyze_process_models_enhanced(),
            "integrations": self._analyze_integrations_enhanced(),
            "security": self._analyze_security_enhanced(),
            "expression_rules": self._extract_expression_rules()
        }
    
    def _analyze_application_info(self) -> Dict:
        """Analyze application information"""
        app_dir = self.extract_dir / "application"
        if not app_dir.exists():
            return {}
        
        for xml_file in app_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                app_elem = root.find(".//application")
                if app_elem is not None:
                    return {
                        "name": app_elem.get("name", ""),
                        "description": self._get_text(app_elem, "description"),
                        "uuid": app_elem.get("uuid", "")
                    }
            except ET.ParseError:
                continue
        
        return {}
    
    def _analyze_sites_enhanced(self) -> List[Dict]:
        """Enhanced site analysis with page hierarchy and UI objects"""
        site_dir = self.extract_dir / "site"
        if not site_dir.exists():
            return []
        
        sites = []
        for xml_file in site_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                site_elem = root.find(".//site")
                if site_elem is not None:
                    site_info = {
                        "uuid": site_elem.get("uuid", ""),
                        "name": site_elem.get("name", ""),
                        "description": self._get_text(site_elem, "description"),
                        "pages": self._extract_site_pages_enhanced(site_elem)
                    }
                    sites.append(site_info)
                    
            except ET.ParseError:
                continue
        
        return sites
    
    def _extract_site_pages_enhanced(self, site_elem: ET.Element) -> List[Dict]:
        """Extract site pages with UI objects and visibility expressions"""
        pages = []
        
        for page_elem in site_elem.findall(".//page"):
            page_uuid = page_elem.get("uuid", "")
            
            # Extract UI object
            ui_object_elem = page_elem.find(".//uiObject")
            ui_object_uuid = ui_object_elem.get("uuid") if ui_object_elem is not None else ""
            ui_object_name = self._resolve_object_name(ui_object_uuid)
            
            # Extract visibility expression
            visibility_expr = self._get_text(page_elem, "visibilityExpr")
            expression_rules = self._extract_expression_rule_uuids(visibility_expr)
            
            page_info = {
                "uuid": page_uuid,
                "name": self._get_text(page_elem, "nameExpr"),
                "ui_object": {
                    "uuid": ui_object_uuid,
                    "name": ui_object_name,
                    "type": self._get_object_type_by_uuid(ui_object_uuid)
                },
                "visibility": {
                    "expression": visibility_expr,
                    "expression_rules": expression_rules
                },
                "url_stub": self._get_text(page_elem, "urlStub")
            }
            
            pages.append(page_info)
        
        return pages
    
    def _extract_expression_rule_uuids(self, expression: str) -> List[Dict]:
        """Extract expression rule UUIDs from expressions"""
        if not expression:
            return []
        
        # Pattern to match expression rule calls: #"uuid"()
        pattern = r'#"([a-f0-9-_]+)"'
        matches = re.findall(pattern, expression)
        
        expression_rules = []
        for uuid in matches:
            rule_name = self._resolve_object_name(uuid)
            expression_rules.append({
                "uuid": uuid,
                "name": rule_name,
                "type": "Expression Rule"
            })
        
        return expression_rules
    
    def _resolve_object_name(self, uuid: str) -> str:
        """Resolve object name from UUID using lookup table"""
        if uuid in self.object_lookup:
            return self.object_lookup[uuid]["name"]
        return f"Unknown ({uuid[:8]}...)"
    
    def _get_object_type_by_uuid(self, uuid: str) -> str:
        """Get object type by UUID"""
        if uuid in self.object_lookup:
            return self.object_lookup[uuid]["type"]
        return "Unknown"
    
    def _analyze_data_model_enhanced(self) -> Dict:
        """Enhanced CDT analysis with relationships and table mappings"""
        # Implementation for enhanced CDT analysis
        return {}
    
    def _analyze_record_types_enhanced(self) -> List[Dict]:
        """Enhanced record type analysis with actions and relationships"""
        # Implementation for enhanced record type analysis
        return []
    
    def _analyze_process_models_enhanced(self) -> List[Dict]:
        """Enhanced process model analysis with nodes and business logic"""
        # Implementation for enhanced process model analysis
        return []
    
    def _analyze_integrations_enhanced(self) -> List[Dict]:
        """Enhanced integration analysis"""
        # Implementation for enhanced integration analysis
        return []
    
    def _analyze_security_enhanced(self) -> List[Dict]:
        """Enhanced security analysis"""
        # Implementation for enhanced security analysis
        return []
    
    def _extract_expression_rules(self) -> Dict:
        """Extract all expression rules referenced in the application"""
        return self.expression_rules
    
    def _generate_human_readable_blueprint(self):
        """Generate human-readable blueprint with actual names"""
        readable_blueprint = self._convert_uuids_to_names(self.blueprint)
        
        # Save human-readable blueprint
        readable_file = self.output_dir / f"{self.zip_path.stem}_readable_blueprint.json"
        with open(readable_file, 'w') as f:
            json.dump(readable_blueprint, f, indent=2)
        
        print(f"📖 Human-readable blueprint saved to {readable_file}")
    
    def _convert_uuids_to_names(self, data: Any) -> Any:
        """Recursively convert UUIDs to human-readable names"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == "uuid" and isinstance(value, str) and value in self.object_lookup:
                    result[key] = f"{self.object_lookup[value]['name']} ({value[:8]})"
                else:
                    result[key] = self._convert_uuids_to_names(value)
            return result
        elif isinstance(data, list):
            return [self._convert_uuids_to_names(item) for item in data]
        else:
            return data
    
    def _cleanup(self):
        """Clean up extracted files"""
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
    
    def save_blueprint(self, output_file: Optional[str] = None) -> str:
        """Save enhanced blueprint"""
        if output_file is None:
            output_file = self.output_dir / f"{self.zip_path.stem}_enhanced_blueprint.json"
        else:
            output_file = self.output_dir / output_file
        
        with open(output_file, 'w') as f:
            json.dump(self.blueprint, f, indent=2)
        
        print(f"💾 Enhanced blueprint saved to {output_file}")
        return str(output_file)

def main():
    """Test the enhanced analyzer"""
    zip_path = "applicationZips/RequirementsManagementv2.3.0.zip"
    
    if not Path(zip_path).exists():
        print(f"❌ Zip file not found: {zip_path}")
        return
    
    analyzer = EnhancedAppianAnalyzer(zip_path)
    blueprint = analyzer.analyze()
    analyzer.save_blueprint()

if __name__ == "__main__":
    main()
