from typing import List, Dict, Any
from pathlib import Path
from . import BaseParser

class ActionParser(BaseParser):
    """Parser for Record Actions - the starting point of user interactions"""
    
    def __init__(self, extract_dir: Path):
        super().__init__(extract_dir)
        self.interfaces_cache = {}
        self.process_models_cache = {}
    
    def parse(self, record_actions: List[Dict]) -> Dict[str, Any]:
        """Parse all record actions with their interfaces and process models"""
        actions_analysis = {
            "actions": [],
            "interface_dependencies": {},
            "process_dependencies": {},
            "security_patterns": {},
            "coverage_analysis": {}
        }
        
        for record_action in record_actions:
            action_analysis = self._analyze_action(record_action)
            if action_analysis:
                actions_analysis["actions"].append(action_analysis)
        
        # Analyze dependencies and patterns
        actions_analysis["interface_dependencies"] = self._analyze_interface_dependencies()
        actions_analysis["process_dependencies"] = self._analyze_process_dependencies()
        actions_analysis["security_patterns"] = self._analyze_security_patterns(actions_analysis["actions"])
        actions_analysis["coverage_analysis"] = self._calculate_coverage_analysis(actions_analysis["actions"])
        
        return actions_analysis
    
    def _analyze_action(self, record_action: Dict) -> Dict[str, Any]:
        """Analyze individual record action"""
        action_name = record_action.get("name", "")
        interface_ref = record_action.get("interface", "")
        process_ref = record_action.get("process_model", "")
        
        if not action_name:
            return None
        
        action_analysis = {
            "name": action_name,
            "security": record_action.get("security", {}),
            "interface_analysis": {},
            "process_analysis": {},
            "dependencies": {
                "interfaces": [],
                "process_models": [],
                "constants": [],
                "expression_rules": [],
                "data_types": []
            },
            "business_logic": {
                "validations": [],
                "business_rules": [],
                "instructions": []
            }
        }
        
        # Analyze interface
        if interface_ref:
            action_analysis["interface_analysis"] = self._analyze_interface(interface_ref)
            action_analysis["dependencies"]["interfaces"] = self._get_interface_dependencies(interface_ref)
        
        # Analyze process model
        if process_ref:
            action_analysis["process_analysis"] = self._analyze_process_model(process_ref)
            action_analysis["dependencies"]["process_models"] = self._get_process_dependencies(process_ref)
        
        return action_analysis
    
    def _analyze_interface(self, interface_ref: str) -> Dict[str, Any]:
        """Analyze interface object in detail"""
        if interface_ref in self.interfaces_cache:
            return self.interfaces_cache[interface_ref]
        
        # Find interface file
        interface_file = self._find_interface_file(interface_ref)
        if not interface_file:
            return {"error": f"Interface file not found: {interface_ref}"}
        
        root = self.safe_parse_xml(interface_file)
        if root is None:
            return {"error": f"Could not parse interface: {interface_ref}"}
        
        interface_analysis = {
            "name": interface_ref,
            "file": interface_file.name,
            "components": self._extract_interface_components(root),
            "called_interfaces": self._extract_called_interfaces(root),
            "constants_used": self._extract_constants_usage(root),
            "expression_rules_used": self._extract_expression_rules_usage(root),
            "data_types_used": self._extract_data_types_usage(root),
            "business_rules": self._extract_interface_business_rules(root),
            "validations": self._extract_interface_validations(root)
        }
        
        self.interfaces_cache[interface_ref] = interface_analysis
        return interface_analysis
    
    def _analyze_process_model(self, process_ref: str) -> Dict[str, Any]:
        """Analyze process model in detail"""
        if process_ref in self.process_models_cache:
            return self.process_models_cache[process_ref]
        
        # Find process model file
        process_file = self._find_process_file(process_ref)
        if not process_file:
            return {"error": f"Process model file not found: {process_ref}"}
        
        root = self.safe_parse_xml(process_file)
        if root is None:
            return {"error": f"Could not parse process model: {process_ref}"}
        
        # Extract actual process name from XML
        namespaces = {'a': 'http://www.appian.com/ae/types/2009'}
        pm_name_element = root.find(".//a:pm/a:meta/a:name/a:string-map/a:pair/a:value", namespaces)
        actual_name = pm_name_element.text if pm_name_element is not None else process_ref
        
        process_analysis = {
            "name": actual_name,
            "file": process_file.name,
            "nodes": self._extract_process_nodes(root),
            "called_processes": self._extract_called_processes(root),
            "interfaces_used": self._extract_process_interfaces(root),
            "expression_rules_used": self._extract_process_expression_rules(root),
            "business_rules": self._extract_process_business_rules(root),
            "flow_analysis": self._analyze_process_flow(root)
        }
        
        self.process_models_cache[process_ref] = process_analysis
        return process_analysis
    
    def _find_interface_file(self, interface_ref: str) -> Path:
        """Find interface file in content directory"""
        content_dir = self.extract_dir / "content"
        if not content_dir.exists():
            return None
        
        # Search for interface file (could be in subdirectories)
        for xml_file in content_dir.rglob("*.xml"):
            if interface_ref in xml_file.name or interface_ref in xml_file.stem:
                return xml_file
        
        return None
    
    def _find_process_file(self, process_ref: str) -> Path:
        """Find process model file"""
        pm_dir = self.extract_dir / "processModel"
        if not pm_dir.exists():
            return None
        
        for xml_file in pm_dir.glob("*.xml"):
            root = self.safe_parse_xml(xml_file)
            if root is not None:
                # Check for process model name in different locations
                name = self.get_text(root, ".//name")
                uuid = self.get_text(root, ".//uuid") 
                version_uuid = self.get_text(root, ".//versionUuid")
                
                # Also check if process_ref is in filename
                if (name == process_ref or 
                    uuid == process_ref or 
                    version_uuid == process_ref or
                    process_ref in xml_file.stem):
                    return xml_file
        
        return None
    
    def _extract_interface_components(self, root) -> List[Dict[str, Any]]:
        """Extract UI components from interface"""
        components = []
        
        # Look for common Appian interface components
        component_types = [
            "a!textField", "a!dropdownField", "a!checkboxField", 
            "a!dateField", "a!fileUploadField", "a!gridField",
            "a!sectionLayout", "a!columnsLayout", "a!cardLayout"
        ]
        
        # This is a simplified extraction - real implementation would need
        # to parse the SAIL expression language
        for comp_type in component_types:
            # Count occurrences (simplified approach)
            content = str(root.text) if root.text else ""
            count = content.count(comp_type)
            if count > 0:
                components.append({
                    "type": comp_type,
                    "count": count
                })
        
        return components
    
    def _extract_called_interfaces(self, root) -> List[str]:
        """Extract interfaces called from this interface"""
        called_interfaces = []
        
        # Look for rule! calls to other interfaces
        # This would need proper SAIL parsing in real implementation
        content = str(root.text) if root.text else ""
        
        # Simple pattern matching for rule! calls
        import re
        rule_pattern = r'rule!\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(rule_pattern, content)
        
        for match in matches:
            if "interface" in match.lower() or "form" in match.lower():
                called_interfaces.append(match)
        
        return list(set(called_interfaces))
    
    def _extract_constants_usage(self, root) -> List[str]:
        """Extract constants used in interface"""
        constants = []
        
        content = str(root.text) if root.text else ""
        
        # Look for cons! references
        import re
        const_pattern = r'cons!\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(const_pattern, content)
        
        return list(set(matches))
    
    def _extract_expression_rules_usage(self, root) -> List[str]:
        """Extract expression rules used in interface"""
        expression_rules = []
        
        content = str(root.text) if root.text else ""
        
        # Look for rule! references that are not interfaces
        import re
        rule_pattern = r'rule!\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(rule_pattern, content)
        
        for match in matches:
            if "interface" not in match.lower() and "form" not in match.lower():
                expression_rules.append(match)
        
        return list(set(expression_rules))
    
    def _extract_data_types_usage(self, root) -> List[str]:
        """Extract data types used in interface"""
        data_types = []
        
        content = str(root.text) if root.text else ""
        
        # Look for type! references
        import re
        type_pattern = r'type!\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(type_pattern, content)
        
        return list(set(matches))
    
    def _extract_interface_business_rules(self, root) -> List[str]:
        """Extract business rules from interface"""
        # This would extract validation rules, conditional logic, etc.
        # Simplified implementation
        return []
    
    def _extract_interface_validations(self, root) -> List[str]:
        """Extract validation rules from interface"""
        # This would extract field validations, form validations, etc.
        # Simplified implementation
        return []
    
    def _extract_process_nodes(self, root) -> List[Dict[str, Any]]:
        """Extract business logic and rules from process nodes (simplified)"""
        business_logic = []
        
        # Define namespace for Appian process models
        namespaces = {'a': 'http://www.appian.com/ae/types/2009'}
        
        # Find nodes with namespace-aware search
        found_nodes = root.findall(".//a:nodes/a:node", namespaces)
        
        for node in found_nodes:
            # Extract only business-relevant information
            node_uuid = self.get_attribute(node, "uuid")
            
            # Extract name
            fname_element = node.find("a:fname/a:string-map/a:pair/a:value", namespaces)
            name = fname_element.text if fname_element is not None else ""
            
            # Skip start/end nodes - no business logic
            if not name or name.lower() in ['start', 'end', 'start node', 'end node']:
                continue
            
            logic_entry = {
                "node_name": name.strip(),
                "uuid": node_uuid
            }
            
            # Extract script/expression logic
            script_element = node.find("a:script", namespaces)
            if script_element is not None and script_element.text:
                logic_entry["script"] = script_element.text.strip()
                logic_entry["type"] = "script"
            
            # Extract interface reference (for user input)
            form_element = node.find(".//form")
            if form_element is not None:
                interface_info = form_element.find(".//a:interfaceInformation/a:name", namespaces)
                if interface_info is not None and interface_info.text:
                    logic_entry["interface"] = interface_info.text.strip()
                    logic_entry["type"] = "userInput"
            
            # Extract expressions from various locations
            expressions = []
            for expr_elem in node.findall(".//expression"):
                if expr_elem.text and expr_elem.text.strip():
                    expressions.append(expr_elem.text.strip())
            
            if expressions:
                logic_entry["expressions"] = expressions
            
            # Only add if there's actual business logic
            if any(key in logic_entry for key in ['script', 'interface', 'expressions']):
                business_logic.append(logic_entry)
        
        return business_logic
    
    def _extract_called_processes(self, root) -> List[str]:
        """Extract process models called from this process"""
        called_processes = []
        
        # Look for subprocess calls
        for node in self.find_all(root, ".//node[@type='subProcess']"):
            subprocess_ref = self.get_text(node, ".//processModel")
            if subprocess_ref:
                called_processes.append(subprocess_ref)
        
        return called_processes
    
    def _extract_process_interfaces(self, root) -> List[str]:
        """Extract interfaces used in process model"""
        interfaces = []
        
        # Define namespace
        namespaces = {'a': 'http://www.appian.com/ae/types/2009'}
        
        # Look for interfaces in interfaceInformation/name elements with namespace
        interface_info_elements = root.findall(".//a:interfaceInformation/a:name", namespaces)
        for elem in interface_info_elements:
            if elem.text:
                interfaces.append(elem.text.strip())
        
        return list(set(interfaces))  # Remove duplicates
    
    def _extract_process_expression_rules(self, root) -> List[str]:
        """Extract expression rules used in process model"""
        expression_rules = []
        
        # Look for script tasks and expressions
        for node in self.find_all(root, ".//node[@type='scriptTask']"):
            expression = self.get_text(node, ".//expression")
            if expression:
                # Extract rule! calls from expression
                import re
                rule_pattern = r'rule!\s*([a-zA-Z_][a-zA-Z0-9_]*)'
                matches = re.findall(rule_pattern, expression)
                expression_rules.extend(matches)
        
        return list(set(expression_rules))
    
    def _extract_process_business_rules(self, root) -> List[str]:
        """Extract business rules configured in process model"""
        # This would extract decision logic, gateway conditions, etc.
        # Simplified implementation
        return []
    
    def _analyze_process_flow(self, root) -> Dict[str, Any]:
        """Analyze process flow and complexity"""
        nodes = self.find_all(root, ".//node")
        gateways = [n for n in nodes if "gateway" in self.get_attribute(n, "type").lower()]
        
        return {
            "total_nodes": len(nodes),
            "decision_points": len(gateways),
            "complexity_score": len(nodes) + len(gateways) * 2
        }
    
    def _get_interface_dependencies(self, interface_ref: str) -> List[str]:
        """Get all dependencies for an interface"""
        if interface_ref not in self.interfaces_cache:
            self._analyze_interface(interface_ref)
        
        interface_data = self.interfaces_cache.get(interface_ref, {})
        dependencies = []
        
        dependencies.extend(interface_data.get("called_interfaces", []))
        dependencies.extend(interface_data.get("constants_used", []))
        dependencies.extend(interface_data.get("expression_rules_used", []))
        dependencies.extend(interface_data.get("data_types_used", []))
        
        return dependencies
    
    def _get_process_dependencies(self, process_ref: str) -> List[str]:
        """Get all dependencies for a process model"""
        if process_ref not in self.process_models_cache:
            self._analyze_process_model(process_ref)
        
        process_data = self.process_models_cache.get(process_ref, {})
        dependencies = []
        
        dependencies.extend(process_data.get("called_processes", []))
        dependencies.extend(process_data.get("interfaces_used", []))
        dependencies.extend(process_data.get("expression_rules_used", []))
        
        return dependencies
    
    def _analyze_interface_dependencies(self) -> Dict[str, List[str]]:
        """Analyze interface dependency graph"""
        return {interface: deps for interface, deps in 
                [(k, v.get("called_interfaces", [])) for k, v in self.interfaces_cache.items()]}
    
    def _analyze_process_dependencies(self) -> Dict[str, List[str]]:
        """Analyze process model dependency graph"""
        return {process: deps for process, deps in 
                [(k, v.get("called_processes", [])) for k, v in self.process_models_cache.items()]}
    
    def _analyze_security_patterns(self, actions: List[Dict]) -> Dict[str, Any]:
        """Analyze security patterns across actions"""
        security_patterns = {
            "group_usage": {},
            "visibility_patterns": [],
            "access_control_complexity": "Low"
        }
        
        for action in actions:
            security = action.get("security", {})
            groups = security.get("groups", [])
            
            for group in groups:
                security_patterns["group_usage"][group] = security_patterns["group_usage"].get(group, 0) + 1
        
        return security_patterns
    
    def _calculate_coverage_analysis(self, actions: List[Dict]) -> Dict[str, Any]:
        """Calculate how much of the application is covered by actions"""
        return {
            "total_actions": len(actions),
            "actions_with_interfaces": len([a for a in actions if a.get("interface_analysis")]),
            "actions_with_processes": len([a for a in actions if a.get("process_analysis")]),
            "estimated_coverage": "70-80%" if len(actions) > 5 else "Partial"
        }
