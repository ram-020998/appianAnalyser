import zipfile
import shutil
import json
from pathlib import Path
from typing import Optional

from .models import ApplicationBlueprint, ComplexityLevel, ApplicationType
from .parsers.data_model_parser import DataModelParser
from .parsers.security_parser import SecurityParser
from .parsers.site_parser import SiteParser
from .parsers.action_parser import ActionParser
from .parsers.integration_parser import IntegrationParser
from .analyzers.blueprint_analyzer import BlueprintAnalyzer
from .analyzers.q_generator import QPromptGenerator

class AppianAnalyzer:
    """Enhanced Appian analyzer following proper Appian analysis methodology"""
    
    def __init__(self, zip_path: str, extract_dir: str = "temp_extract", output_dir: str = "output"):
        self.zip_path = Path(zip_path)
        self.extract_dir = Path(extract_dir)
        self.output_dir = Path(output_dir)
        self.blueprint: Optional[ApplicationBlueprint] = None
        self.analysis_data = {}
        
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze(self) -> ApplicationBlueprint:
        """Perform comprehensive analysis following Appian methodology"""
        print(f"🔍 Analyzing Appian application: {self.zip_path.name}")
        print("📋 Following Appian analysis methodology...")
        
        try:
            self._extract_application()
            app_info = self._parse_application_metadata()
            
            self.blueprint = ApplicationBlueprint(
                name=app_info.get("name", "Unknown Application"),
                description=app_info.get("description", ""),
                version=app_info.get("version", "1.0"),
                complexity=ComplexityLevel.MEDIUM,
                app_type=ApplicationType.HYBRID
            )
            
            print("📊 Step 1: Analyzing Data Model...")
            self._analyze_data_model()
            
            print("🔒 Step 2: Analyzing Security Groups...")
            self._analyze_security_groups()
            
            print("🏠 Step 3: Analyzing Sites and Navigation...")
            self._analyze_sites_and_navigation()
            
            print("⚡ Step 4: Analyzing Actions and Workflows...")
            self._analyze_actions()
            
            print("🔗 Step 5: Analyzing Integration Objects...")
            self._analyze_integrations()
            
            print("🧠 Generating insights and recommendations...")
            self._generate_final_analysis()
            
            print("✅ Comprehensive analysis complete!")
            return self.blueprint
            
        finally:
            self._cleanup()
    
    def _extract_application(self):
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
        self.extract_dir.mkdir(parents=True)
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_dir)
        print(f"📦 Extracted to {self.extract_dir}")
    
    def _parse_application_metadata(self) -> dict:
        app_dir = self.extract_dir / "application"
        if not app_dir.exists():
            return {}
        
        for xml_file in app_dir.glob("*.xml"):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                app_elem = root.find(".//application")
                if app_elem is not None:
                    return {
                        "name": self._get_text(app_elem, "name"),
                        "description": self._get_text(app_elem, "description"),
                        "version": self._get_text(app_elem, "version", "1.0"),
                        "uuid": self._get_text(app_elem, "uuid")
                    }
            except ET.ParseError:
                continue
        return {}
    
    def _analyze_data_model(self):
        parser = DataModelParser(self.extract_dir)
        data_model = parser.parse()
        self.analysis_data["data_model"] = data_model
        
        print(f"  📋 Found {len(data_model['cdts'])} CDTs")
        print(f"  📄 Found {len(data_model['record_types'])} Record Types")
        print(f"  🔗 Found {len(data_model['relationships'])} relationships")
        if len(data_model["duplicates"]) > 0:
            print(f"  ⚠️  Found {len(data_model['duplicates'])} potential duplicate entities")
    
    def _analyze_security_groups(self):
        parser = SecurityParser(self.extract_dir)
        security_groups = parser.parse()
        
        self.analysis_data["security_groups_raw"] = security_groups
        self.blueprint.security_groups = security_groups
        
        print(f"  🔒 Found {len(security_groups)} security groups")
        
        group_types = {}
        for group in security_groups:
            group_type = group.type
            group_types[group_type] = group_types.get(group_type, 0) + 1
        
        for group_type, count in group_types.items():
            print(f"    - {group_type}: {count} groups")
    
    def _analyze_sites_and_navigation(self):
        parser = SiteParser(self.extract_dir)
        site_data = parser.parse()
        self.analysis_data["sites"] = site_data
        
        sites = site_data["sites"]
        navigation = site_data["navigation_structure"]
        
        print(f"  🏠 Found {len(sites)} sites")
        print(f"  📑 Total tabs: {navigation.get('total_tabs', 0)}")
        print(f"  📄 Total pages: {navigation.get('total_pages', 0)}")
    
    def _analyze_actions(self):
        record_actions = []
        data_model = self.analysis_data.get("data_model", {})
        
        for record_type in data_model.get("record_types", []):
            actions = record_type.get("actions", [])
            for action in actions:
                action["record_type"] = record_type["name"]
                record_actions.append(action)
        
        if not record_actions:
            print("  ⚠️  No record actions found - analyzing available interfaces and processes")
            self._analyze_standalone_objects()
            return
        
        parser = ActionParser(self.extract_dir)
        actions_analysis = parser.parse(record_actions)
        self.analysis_data["actions"] = actions_analysis
        
        actions = actions_analysis["actions"]
        print(f"  ⚡ Found {len(actions)} record actions")
    
    def _analyze_standalone_objects(self):
        content_dir = self.extract_dir / "content"
        process_dir = self.extract_dir / "processModel"
        
        interface_count = len(list(content_dir.rglob("*.xml"))) if content_dir.exists() else 0
        process_count = len(list(process_dir.glob("*.xml"))) if process_dir.exists() else 0
        
        print(f"  📱 Found {interface_count} interface objects")
        print(f"  ⚙️  Found {process_count} process model objects")
        
        self.analysis_data["standalone_objects"] = {
            "interfaces": interface_count,
            "processes": process_count
        }
    
    def _analyze_integrations(self):
        parser = IntegrationParser(self.extract_dir)
        integrations = parser.parse()
        
        self.analysis_data["integrations_raw"] = integrations
        self.blueprint.integrations = integrations
        
        print(f"  🔗 Found {len(integrations)} integration points")
        
        patterns = {}
        for integration in integrations:
            pattern = integration.pattern
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        for pattern, count in patterns.items():
            print(f"    - {pattern}: {count} integrations")
    
    def _generate_final_analysis(self):
        analyzer = BlueprintAnalyzer(self.blueprint)
        analyzer.analysis_data = self.analysis_data
        analyzer.analyze()
        
        print(f"  📈 Application Type: {self.blueprint.app_type.value}")
        print(f"  📊 Complexity: {self.blueprint.complexity.value}")
        print(f"  🎯 Recommendations: {len(self.blueprint.recommendations)}")
    
    def _get_text(self, element, xpath: str, default: str = "") -> str:
        try:
            found = element.find(xpath)
            return found.text.strip() if found is not None and found.text else default
        except Exception:
            return default
    
    def _cleanup(self):
        if self.extract_dir.exists():
            shutil.rmtree(self.extract_dir)
    
    def save_blueprint(self, output_file: Optional[str] = None) -> str:
        if not self.blueprint:
            raise ValueError("No blueprint available. Run analyze() first.")
        
        if output_file is None:
            output_file = self.output_dir / f"{self.zip_path.stem}_blueprint.json"
        else:
            output_file = self.output_dir / output_file
        
        blueprint_data = self.blueprint.to_dict()
        
        # Add serializable analysis data
        serializable_analysis = {}
        for key, value in self.analysis_data.items():
            if key == "security_groups_raw":
                serializable_analysis["security_groups"] = [
                    {
                        "name": sg.name,
                        "uuid": sg.uuid,
                        "type": sg.type,
                        "business_function": sg.business_function,
                        "member_count": sg.member_count
                    } for sg in value
                ]
            elif key == "integrations_raw":
                serializable_analysis["integrations"] = [
                    {
                        "name": ip.name,
                        "type": ip.type,
                        "pattern": ip.pattern,
                        "security_level": ip.security_level,
                        "endpoints": ip.endpoints
                    } for ip in value
                ]
            else:
                serializable_analysis[key] = value
        
        blueprint_data["detailed_analysis"] = serializable_analysis
        
        with open(output_file, 'w') as f:
            json.dump(blueprint_data, f, indent=2)
        
        print(f"💾 Enhanced blueprint saved to {output_file}")
        return str(output_file)
    
    def generate_q_prompt(self, output_file: Optional[str] = None) -> str:
        if not self.blueprint:
            raise ValueError("No blueprint available. Run analyze() first.")
        
        if output_file is None:
            output_file = self.output_dir / f"{self.zip_path.stem}_q_prompt.txt"
        else:
            output_file = self.output_dir / output_file
        
        generator = QPromptGenerator(self.blueprint)
        generator.analysis_data = self.analysis_data
        prompt = generator.generate()
        
        with open(output_file, 'w') as f:
            f.write(prompt)
        
        print(f"📝 Comprehensive Q prompt saved to {output_file}")
        return str(output_file)
