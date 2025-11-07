"""
SAIL Code Formatter - Formats and cleans SAIL code with UUID resolution
"""
import re
from typing import Dict, Any

class SAILFormatter:
    """Formats SAIL code by resolving UUIDs and cleaning formatting"""
    
    def __init__(self, object_lookup: Dict[str, Dict[str, Any]]):
        self.object_lookup = object_lookup
    
    def format_sail_code(self, sail_code: str) -> str:
        """Format SAIL code with UUID resolution and cleanup"""
        if not sail_code or not sail_code.strip():
            return ""
        
        # Step 1: Remove escape sequences
        formatted_code = self._remove_escape_sequences(sail_code)
        
        # Step 2: Replace UUID references with object names
        formatted_code = self._replace_uuid_references(formatted_code)
        
        # Step 3: Clean up formatting
        formatted_code = self._clean_formatting(formatted_code)
        
        return formatted_code
    
    def format_process_model_logic(self, business_logic: str) -> str:
        """Format process model business logic with proper node separation"""
        if not business_logic or not business_logic.strip():
            return ""
        
        # Step 1: Remove escape sequences
        formatted_logic = self._remove_escape_sequences(business_logic)
        
        # Step 2: Replace UUID references
        formatted_logic = self._replace_uuid_references(formatted_logic)
        
        # Step 3: Format node sections with proper line breaks
        formatted_logic = self._format_node_sections(formatted_logic)
        
        return formatted_logic
    
    def _remove_escape_sequences(self, code: str) -> str:
        """Remove escape sequences while preserving content"""
        # Remove common escape sequences
        code = code.replace('\\n', '\n')
        code = code.replace('\\t', '\t')
        code = code.replace('\\r', '\r')
        code = code.replace('\\"', '"')
        code = code.replace("\\'", "'")
        code = code.replace('\\\\', '\\')
        
        return code
    
    def _replace_uuid_references(self, code: str) -> str:
        """Replace UUID references with actual object names"""
        # Pattern to match UUID references like #"_a-uuid" or #"uuid"
        uuid_pattern = r'#"(_a-[a-f0-9\-_]+)"'
        
        def replace_uuid(match):
            uuid = match.group(1)
            obj = self.object_lookup.get(uuid)
            if obj:
                object_name = obj.get('name', uuid)
                # Return in a readable format
                return f'rule!{object_name}'
            return match.group(0)  # Return original if not found
        
        return re.sub(uuid_pattern, replace_uuid, code)
    
    def _clean_formatting(self, code: str) -> str:
        """Clean up code formatting"""
        # Remove excessive whitespace while preserving structure
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace but preserve indentation
            cleaned_line = line.rstrip()
            if cleaned_line or (cleaned_lines and cleaned_lines[-1].strip()):
                cleaned_lines.append(cleaned_line)
        
        # Remove excessive empty lines (more than 2 consecutive)
        result_lines = []
        empty_count = 0
        
        for line in cleaned_lines:
            if line.strip():
                result_lines.append(line)
                empty_count = 0
            else:
                empty_count += 1
                if empty_count <= 2:
                    result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _format_node_sections(self, logic: str) -> str:
        """Format process model node sections with proper separation"""
        # Split by node headers and reformat
        node_sections = re.split(r'(=== NODE: [^=]+ ===)', logic)
        
        formatted_sections = []
        for i, section in enumerate(node_sections):
            if section.startswith('=== NODE:'):
                # This is a node header
                formatted_sections.append(f'\n{section}\n')
            elif section.strip():
                # This is node content - format with proper line breaks
                lines = section.strip().split('\n')
                formatted_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        # Add proper indentation for readability
                        if ':' in line and not line.startswith('  '):
                            formatted_lines.append(f'  {line}')
                        else:
                            formatted_lines.append(f'    {line}')
                
                if formatted_lines:
                    formatted_sections.append('\n'.join(formatted_lines))
        
        return ''.join(formatted_sections).strip()
