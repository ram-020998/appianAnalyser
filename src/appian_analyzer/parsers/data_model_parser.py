from typing import List, Dict, Any
from pathlib import Path
from . import BaseParser

class DataModelParser(BaseParser):
    """Enhanced parser for both CDTs and Record Types following Appian best practices"""
    
    def __init__(self, extract_dir: Path):
        super().__init__(extract_dir)
        # Add Appian namespace
        self.namespaces['a'] = 'http://www.appian.com/ae/types/2009'
    
    def parse(self) -> Dict[str, Any]:
        """Parse complete data model including CDTs and Record Types"""
        data_model = {
            "cdts": self._parse_cdts(),
            "record_types": self._parse_record_types(),
            "data_entities": [],
            "relationships": [],
            "duplicates": []
        }
        
        # Identify data entities and relationships
        data_model["data_entities"] = self._identify_data_entities(
            data_model["cdts"], data_model["record_types"]
        )
        data_model["relationships"] = self._analyze_relationships(data_model["data_entities"])
        data_model["duplicates"] = self._find_duplicate_entities(data_model["data_entities"])
        
        return data_model
    
    def _parse_cdts(self) -> List[Dict[str, Any]]:
        """Parse Custom Data Types (CDTs)"""
        datatype_dir = self.extract_dir / "datatype"
        if not datatype_dir.exists():
            return []
        
        cdts = []
        for xsd_file in datatype_dir.glob("*.xsd"):
            if "deprecated" in xsd_file.name.lower():
                continue
                
            cdt_data = self._parse_cdt_file(xsd_file)
            if cdt_data:
                cdts.extend(cdt_data)
        
        return cdts
    
    def _parse_record_types(self) -> List[Dict[str, Any]]:
        """Parse Record Types (new version of CDTs)"""
        record_dir = self.extract_dir / "recordType"
        if not record_dir.exists():
            return []
        
        records = []
        for xml_file in record_dir.glob("*.xml"):
            if "deprecated" in xml_file.name.lower():
                continue
                
            record_data = self._parse_record_file(xml_file)
            if record_data:
                records.append(record_data)
        
        return records
    
    def _parse_cdt_file(self, xsd_file: Path) -> List[Dict[str, Any]]:
        """Parse individual CDT file"""
        root = self.safe_parse_xml(xsd_file)
        if root is None:
            return []
        
        cdts = []
        
        try:
            complex_types = root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
        except Exception:
            try:
                complex_types = root.findall(".//complexType")
            except Exception:
                complex_types = []
        
        for ct in complex_types:
            type_name = ct.get("name")
            if not type_name:
                continue
            
            table_name = self._extract_table_name(ct)
            fields = self._extract_cdt_fields(ct)
            
            cdt = {
                "name": type_name,
                "type": "CDT",
                "table_name": table_name,
                "fields": fields,
                "file": xsd_file.name,
                "namespace": self._extract_namespace(xsd_file.name)
            }
            
            cdts.append(cdt)
        
        return cdts
    
    def _parse_record_file(self, xml_file: Path) -> Dict[str, Any]:
        """Parse individual Record Type file"""
        root = self.safe_parse_xml(xml_file)
        if root is None:
            return None
        
        # Look for recordType element in recordTypeHaul
        record_elem = root.find(".//recordType", self.namespaces)
        if record_elem is None:
            return None
        
        name = record_elem.get("name", "")
        if not name:
            return None
        
        # Extract record type details
        fields = self._extract_record_fields(record_elem)
        relationships = self._extract_record_relationships(record_elem)
        actions = self._extract_all_actions(root)  # Extract both record actions and related actions
        
        return {
            "name": name,
            "type": "Record Type",
            "uuid": record_elem.get("{http://www.appian.com/ae/types/2009}uuid", ""),
            "plural_name": self.get_text(record_elem, "a:pluralName"),
            "description": self.get_text(record_elem, "a:description"),
            "url_stub": self.get_text(record_elem, "a:urlStub"),
            "fields": fields,
            "relationships": relationships,
            "actions": actions,
            "file": xml_file.name
        }
    
    def _extract_table_name(self, complex_type) -> str:
        """Extract database table name from CDT annotations"""
        try:
            annotations = complex_type.findall(".//annotation")
            for annotation in annotations:
                appinfo = annotation.find(".//appinfo")
                if appinfo is not None and appinfo.text:
                    text = appinfo.text
                    if "@Table(name=" in text:
                        start = text.find('name="') + 6
                        end = text.find('"', start)
                        return text[start:end] if start > 5 and end > start else ""
        except Exception:
            pass
        return ""
    
    def _extract_cdt_fields(self, complex_type) -> List[Dict[str, Any]]:
        """Extract fields from CDT"""
        fields = []
        
        try:
            sequences = complex_type.findall(".//sequence")
            for seq in sequences:
                elements = seq.findall(".//element")
                for elem in elements:
                    field_info = {
                        "name": elem.get("name", ""),
                        "type": elem.get("type", ""),
                        "min_occurs": elem.get("minOccurs", "1"),
                        "max_occurs": elem.get("maxOccurs", "1")
                    }
                    
                    if field_info["name"]:
                        fields.append(field_info)
        except Exception:
            pass
        
        return fields
    
    def _extract_record_fields(self, record_elem) -> List[Dict[str, Any]]:
        """Extract fields from Record Type"""
        fields = []
        
        # Look for recordField elements with namespace
        try:
            field_elements = record_elem.findall(".//a:recordField", self.namespaces)
            
            for field_elem in field_elements:
                field_uuid = field_elem.get("{http://www.appian.com/ae/types/2009}uuid", "")
                field_name = field_elem.get("name", "")
                
                if field_name:
                    field = {
                        "uuid": field_uuid,
                        "name": field_name,
                        "type": self.get_text(field_elem, "type"),
                        "required": self.get_text(field_elem, "required") == "true",
                        "multiple": self.get_text(field_elem, "multiple") == "true"
                    }
                    fields.append(field)
        except Exception:
            pass
        
        return fields
    
    def _extract_record_relationships(self, record_elem) -> List[Dict[str, Any]]:
        """Extract relationships from Record Type"""
        relationships = []
        
        try:
            rel_elements = record_elem.findall(".//a:recordRelationship", self.namespaces)
            
            for rel_elem in rel_elements:
                relationship = {
                    "uuid": rel_elem.get("{http://www.appian.com/ae/types/2009}uuid", ""),
                    "name": rel_elem.get("name", ""),
                    "related_record": self.get_text(rel_elem, "relatedRecordType"),
                    "type": self.get_text(rel_elem, "relationshipType")
                }
                
                if relationship["name"]:
                    relationships.append(relationship)
        except Exception:
            pass
        
        return relationships
    
    def _extract_all_actions(self, root) -> List[Dict[str, Any]]:
        """Extract both record actions and related actions"""
        actions = []
        
        # Extract traditional record actions
        actions.extend(self._extract_record_actions(root))
        
        # Extract related actions
        actions.extend(self._extract_related_actions(root))
        
        return actions
    
    def _extract_record_actions(self, root) -> List[Dict[str, Any]]:
        """Extract traditional record actions"""
        actions = []
        
        try:
            action_elements = root.findall(".//a:recordAction", self.namespaces)
            
            for action_elem in action_elements:
                action_uuid = action_elem.get("{http://www.appian.com/ae/types/2009}uuid", "")
                action_name = action_elem.get("name", "")
                
                if action_name:
                    action = {
                        "uuid": action_uuid,
                        "name": action_name,
                        "type": "Record Action",
                        "label": self.get_text(action_elem, "a:label"),
                        "process_model": self.get_text(action_elem, "a:processModel"),
                        "interface": self.get_text(action_elem, "a:interface"),
                        "security": self._extract_action_security(action_elem)
                    }
                    actions.append(action)
        except Exception:
            pass
        
        return actions
    
    def _extract_related_actions(self, root) -> List[Dict[str, Any]]:
        """Extract related actions (relatedActionCfg)"""
        actions = []
        
        try:
            # Look for relatedActionCfg elements with proper namespace
            related_action_elements = root.findall(".//a:relatedActionCfg", self.namespaces)
            
            for action_elem in related_action_elements:
                action_uuid = action_elem.get("{http://www.appian.com/ae/types/2009}uuid", "")
                ref_id = self.get_text(action_elem, "a:refId")
                
                # Extract target information
                target_elem = action_elem.find("a:target", self.namespaces)
                
                if target_elem is not None:
                    target_uuid = target_elem.get("{http://www.appian.com/ae/types/2009}uuid", "")
                    target_type = target_elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
                    
                    # Extract action name from reference or generate from ref_id
                    action_name = self._resolve_action_reference(ref_id) if ref_id else f"Action {action_uuid[:8]}"
                    
                    action = {
                        "uuid": ref_id or action_uuid,
                        "name": action_name,
                        "type": "Related Action",
                        "label": action_name,
                        "reference_id": ref_id,
                        "target_uuid": target_uuid,
                        "target_type": target_type,
                        "process_model": target_uuid if "ProcessModel" in target_type else "",
                        "interface": target_uuid if "Interface" in target_type else "",
                        "security": self._extract_action_security(action_elem)
                    }
                    actions.append(action)
        except Exception:
            pass
        
        return actions
    
    def _resolve_action_reference(self, ref_id: str) -> str:
        """Resolve action reference ID to actual name"""
        # Extract meaningful name from reference ID
        if ref_id.startswith("refId-"):
            # Remove refId- prefix and extract UUID part
            clean_id = ref_id.replace("refId-", "")
            # Split by hyphens and take meaningful parts
            parts = clean_id.split("-")
            if len(parts) >= 6:  # UUID format with suffix
                suffix = parts[-1]  # Last part often contains meaningful info
                if suffix and suffix != "pro":
                    return f"Action {suffix.upper()}"
        
        # Fallback to shortened reference
        return f"Action {ref_id[-8:]}"
    
    def _extract_action_security(self, action_elem) -> Dict[str, Any]:
        """Extract security configuration for actions"""
        return {
            "visibility": self.get_text(action_elem, "a:visibility"),
            "groups": [g.text for g in action_elem.findall(".//group") if g.text]
        }
    
    def _identify_data_entities(self, cdts: List[Dict], records: List[Dict]) -> List[Dict[str, Any]]:
        """Identify all data entities combining CDTs and Record Types"""
        entities = []
        
        for cdt in cdts:
            entities.append({
                "name": cdt["name"],
                "type": "CDT",
                "table_name": cdt.get("table_name", ""),
                "fields": cdt["fields"],
                "source": "datatype"
            })
        
        for record in records:
            entities.append({
                "name": record["name"],
                "type": "Record Type",
                "table_name": record.get("table_name", ""),
                "fields": record["fields"],
                "source": "recordType"
            })
        
        return entities
    
    def _analyze_relationships(self, entities: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze relationships between data entities"""
        relationships = []
        
        for entity in entities:
            for field in entity.get("fields", []):
                field_type = field.get("type", "")
                
                for other_entity in entities:
                    if other_entity["name"] in field_type:
                        relationships.append({
                            "from_entity": entity["name"],
                            "to_entity": other_entity["name"],
                            "field_name": field["name"],
                            "relationship_type": "reference"
                        })
        
        return relationships
    
    def _find_duplicate_entities(self, entities: List[Dict]) -> List[Dict[str, Any]]:
        """Find potential duplicate entities"""
        duplicates = []
        table_map = {}
        
        for entity in entities:
            table_name = entity.get("table_name", "").upper()
            if table_name:
                if table_name not in table_map:
                    table_map[table_name] = []
                table_map[table_name].append(entity)
        
        for table_name, table_entities in table_map.items():
            if len(table_entities) > 1:
                duplicates.append({
                    "table_name": table_name,
                    "entities": [{"name": e["name"], "type": e["type"]} for e in table_entities],
                    "recommendation": "Consider consolidating to single Record Type"
                })
        
        return duplicates
    
    def _extract_namespace(self, filename: str) -> str:
        """Extract namespace from encoded filename"""
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(filename)
            if "urn:com:appian:types:" in decoded:
                parts = decoded.split("urn:com:appian:types:")[1].split("}")[0]
                return parts.replace(":", "_")
        except Exception:
            pass
        return "Unknown"
