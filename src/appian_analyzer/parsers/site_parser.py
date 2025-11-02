from typing import List, Dict, Any
from pathlib import Path
from . import BaseParser

class SiteParser(BaseParser):
    """Parser for Site objects - landing pages and navigation structure"""
    
    def parse(self) -> Dict[str, Any]:
        """Parse site configuration and navigation structure"""
        site_dir = self.extract_dir / "site"
        if not site_dir.exists():
            return {"sites": [], "navigation_structure": {}}
        
        sites = []
        for xml_file in site_dir.glob("*.xml"):
            if "deprecated" in xml_file.name.lower():
                continue
                
            site_data = self._parse_site_file(xml_file)
            if site_data:
                sites.append(site_data)
        
        navigation_structure = self._analyze_navigation_structure(sites)
        
        return {
            "sites": sites,
            "navigation_structure": navigation_structure,
            "primary_site": self._identify_primary_site(sites)
        }
    
    def _parse_site_file(self, xml_file: Path) -> Dict[str, Any]:
        """Parse individual site file"""
        root = self.safe_parse_xml(xml_file)
        if root is None:
            return None
        
        # Look for site element in siteHaul
        site_elem = root.find(".//site")
        if site_elem is None:
            return None
        
        name = site_elem.get("name", "")
        if not name:
            return None
        
        site_data = {
            "name": name,
            "uuid": site_elem.get("uuid", ""),
            "description": self.get_text(site_elem, "description"),
            "url_stub": self.get_text(site_elem, "urlStub"),
            "pages": self._extract_pages(site_elem),
            "file": xml_file.name
        }
        
        return site_data
    
    def _extract_pages(self, site_elem) -> List[Dict[str, Any]]:
        """Extract pages from site"""
        pages = []
        
        # Find all page elements
        page_elements = site_elem.findall(".//page")
        for page_elem in page_elements:
            page_uuid = page_elem.get("uuid", "")
            
            # Extract page name (could be in nameExpr)
            name_expr = self.get_text(page_elem, "nameExpr")
            name = name_expr if name_expr else f"Page_{page_uuid[:8]}"
            
            page = {
                "uuid": page_uuid,
                "name": name,
                "description": self.get_text(page_elem, "description"),
                "url_stub": self.get_text(page_elem, "urlStub"),
                "ui_object": page_elem.find(".//uiObject").get("uuid") if page_elem.find(".//uiObject") is not None else "",
                "icon_id": self.get_text(page_elem, "iconId"),
                "visibility": self.get_text(page_elem, "visibilityExpr")
            }
            
            if page_uuid:
                pages.append(page)
        
        return pages
    
    def _analyze_navigation_structure(self, sites: List[Dict]) -> Dict[str, Any]:
        """Analyze overall navigation structure"""
        structure = {
            "total_sites": len(sites),
            "total_pages": 0,
            "site_breakdown": {}
        }
        
        for site in sites:
            pages = site.get("pages", [])
            structure["total_pages"] += len(pages)
            structure["site_breakdown"][site["name"]] = len(pages)
        
        return structure
    
    def _identify_primary_site(self, sites: List[Dict]) -> Dict[str, Any]:
        """Identify the primary/main site of the application"""
        if not sites:
            return {}
        
        # Primary site is typically the one with most pages or specific naming
        primary_candidates = []
        
        for site in sites:
            score = 0
            name_lower = site["name"].lower()
            
            # Score based on naming patterns
            if any(keyword in name_lower for keyword in ["main", "home", "primary", "dashboard"]):
                score += 10
            
            # Score based on content
            pages = site.get("pages", [])
            score += len(pages) * 2
            
            primary_candidates.append((site, score))
        
        # Return site with highest score
        primary_candidates.sort(key=lambda x: x[1], reverse=True)
        return primary_candidates[0][0] if primary_candidates else {}
