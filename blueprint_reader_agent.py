#!/usr/bin/env python3
"""
Blueprint Reader Agent - Uses Amazon Q to generate human-readable blueprints
"""

import json
import sys
from pathlib import Path

class BlueprintReaderAgent:
    """Amazon Q agent for generating human-readable application blueprints"""
    
    def __init__(self, blueprint_file: str, lookup_file: str = None):
        self.blueprint_file = Path(blueprint_file)
        
        if not self.blueprint_file.exists():
            raise FileNotFoundError(f"Blueprint file not found: {blueprint_file}")
        
        # Auto-detect lookup file if not provided
        if lookup_file is None:
            stem = self.blueprint_file.stem.replace("_enhanced_blueprint", "")
            self.lookup_file = self.blueprint_file.parent / f"{stem}_object_lookup.json"
        else:
            self.lookup_file = Path(lookup_file)
        
        if not self.lookup_file.exists():
            raise FileNotFoundError(f"Object lookup file not found: {self.lookup_file}")
    
    def generate_readable_blueprint(self):
        """Generate human-readable blueprint using Amazon Q"""
        
        # Load the data
        with open(self.blueprint_file, 'r') as f:
            blueprint = json.load(f)
        
        with open(self.lookup_file, 'r') as f:
            lookup_data = json.load(f)
        
        # Create Amazon Q prompt
        prompt = self._create_q_prompt(blueprint, lookup_data)
        
        # Save prompt for Amazon Q
        prompt_file = self.blueprint_file.parent / f"{self.blueprint_file.stem.replace('_enhanced_blueprint', '')}_q_readable_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        
        print(f"🤖 Amazon Q prompt generated: {prompt_file}")
        print(f"\n📋 Next steps:")
        print(f"1. Copy the prompt from: {prompt_file}")
        print(f"2. Paste it into Amazon Q chat")
        print(f"3. Amazon Q will generate a human-readable blueprint document")
        
        return prompt_file
    
    def _create_q_prompt(self, blueprint: dict, lookup_data: dict) -> str:
        """Create optimized prompt for Amazon Q"""
        
        app_name = blueprint.get("application_info", {}).get("name", "Unknown Application")
        summary = blueprint.get("summary", {})
        
        prompt = f"""# Generate Human-Readable Appian Application Blueprint

Please analyze the following Appian application data and generate a comprehensive, human-readable blueprint document in markdown format.

## Application Overview
- **Name**: {app_name}
- **Total Objects**: {lookup_data.get('total_objects', 0)}
- **Sites**: {summary.get('sites_count', 0)}
- **Record Types**: {summary.get('record_types_count', 0)}
- **Actions**: {summary.get('actions_count', 0)}
- **Process Models**: {summary.get('process_models_count', 0)}
- **Data Types**: {summary.get('data_types_count', 0)}
- **Integrations**: {summary.get('integrations_count', 0)}
- **Security Groups**: {summary.get('security_groups_count', 0)}

## Object Lookup Table
```json
{json.dumps(lookup_data, indent=2)[:2000]}...
```

## Enhanced Blueprint Data
```json
{json.dumps(blueprint, indent=2)[:5000]}...
```

## Requirements for Human-Readable Blueprint

Please generate a comprehensive markdown document that includes:

### 1. Executive Summary
- Application purpose and type
- Key business capabilities
- Architecture overview
- Complexity assessment

### 2. Site Architecture
For each site, provide:
- Site name and purpose
- Page hierarchy with descriptions
- UI components and their business functions
- Visibility rules in plain English

### 3. Data Model
For each record type:
- Business purpose and description
- Key fields and their meanings
- Available actions and what they do
- Relationships to other records
- Business workflows supported

### 4. Process Automation
For each process model:
- Business process description
- Key automation steps
- Integration points
- User interaction points

### 5. Integration Architecture
- External system connections
- API endpoints and purposes
- Data flow descriptions
- Security considerations

### 6. Security Model
- Security group purposes
- Access control patterns
- Role-based permissions
- Business function mapping

### 7. Recommendations
- Architecture improvements
- Consolidation opportunities
- Performance optimizations
- Maintenance considerations

**Important**: Use the object lookup table to resolve all UUIDs to meaningful names. Focus on business value and user understanding rather than technical details. Make it readable for business stakeholders, not just developers.
"""
        
        return prompt

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 blueprint_reader_agent.py <blueprint_file> [lookup_file]")
        print("Example: python3 blueprint_reader_agent.py output/app_enhanced_blueprint.json")
        sys.exit(1)
    
    blueprint_file = sys.argv[1]
    lookup_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        agent = BlueprintReaderAgent(blueprint_file, lookup_file)
        agent.generate_readable_blueprint()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
