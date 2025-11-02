from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from pathlib import Path

class BaseParser(ABC):
    """Base class for all Appian XML parsers"""
    
    def __init__(self, extract_dir: Path):
        self.extract_dir = extract_dir
        self.namespaces = {
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'appian': 'http://www.appian.com/ae/types/2009'
        }
    
    @abstractmethod
    def parse(self) -> Any:
        """Parse the specific component type"""
        pass
    
    def safe_parse_xml(self, file_path: Path) -> Optional[ET.Element]:
        """Safely parse XML file with error handling"""
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except (ET.ParseError, FileNotFoundError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return None
    
    def get_text(self, element: ET.Element, xpath: str, default: str = "") -> str:
        """Safely extract text from XML element"""
        try:
            found = element.find(xpath, self.namespaces)
            return found.text.strip() if found is not None and found.text else default
        except Exception:
            return default
    
    def get_attribute(self, element: ET.Element, attr: str, default: str = "") -> str:
        """Safely get attribute value"""
        return element.get(attr, default)
    
    def find_all(self, element: ET.Element, xpath: str) -> List[ET.Element]:
        """Find all elements matching xpath"""
        try:
            return element.findall(xpath, self.namespaces)
        except Exception:
            return []
