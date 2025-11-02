#!/usr/bin/env python3
"""
Amazon Q Blueprint Agent - Invokes Q agent to generate readable blueprints
"""

import json
import subprocess
import sys
from pathlib import Path

class AmazonQBlueprintAgent:
    """Invokes Amazon Q agent for blueprint generation"""
    
    def __init__(self, blueprint_file: str, lookup_file: str):
        self.blueprint_file = Path(blueprint_file)
        self.lookup_file = Path(lookup_file)
        
        if not self.blueprint_file.exists():
            raise FileNotFoundError(f"Blueprint file not found: {blueprint_file}")
        if not self.lookup_file.exists():
            raise FileNotFoundError(f"Lookup file not found: {lookup_file}")
    
    def generate_readable_blueprint(self) -> str:
        """Generate readable blueprint using Amazon Q agent"""
        
        # Load data
        with open(self.blueprint_file, 'r') as f:
            blueprint = json.load(f)
        
        with open(self.lookup_file, 'r') as f:
            lookup_data = json.load(f)
        
        # Create prompt for Q agent
        prompt = self._create_agent_prompt(blueprint, lookup_data)
        
        try:
            # Invoke Amazon Q agent using proper CLI syntax
            print("🤖 Invoking Amazon Q agent...")
            result = subprocess.run([
                'q', 'chat', '--agent', 'appian-blueprint-reader',
                prompt
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Save the generated blueprint
                output_file = self.blueprint_file.parent / f"{self.blueprint_file.stem.replace('_enhanced_blueprint', '')}_readable_blueprint.md"
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                
                print(f"✅ Readable blueprint generated: {output_file}")
                return str(output_file)
            else:
                print(f"❌ Q agent failed: {result.stderr}")
                return self._fallback_generation(blueprint, lookup_data)
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️  Q agent unavailable ({e}), using fallback...")
            return self._fallback_generation(blueprint, lookup_data)
    
    def _create_agent_prompt(self, blueprint: dict, lookup_data: dict) -> str:
        """Create prompt for Amazon Q agent"""
        
        app_name = blueprint.get("application_info", {}).get("name", "Unknown Application")
        summary = blueprint.get("summary", {})
        
        prompt = f"""Generate a comprehensive human-readable blueprint for the Appian application: {app_name}

Application Summary:
- Total Objects: {lookup_data.get('total_objects', 0)}
- Sites: {summary.get('sites_count', 0)}
- Record Types: {summary.get('record_types_count', 0)}
- Actions: {summary.get('actions_count', 0)}
- Process Models: {summary.get('process_models_count', 0)}
- Data Types: {summary.get('data_types_count', 0)}
- Integrations: {summary.get('integrations_count', 0)}
- Security Groups: {summary.get('security_groups_count', 0)}

Object Lookup Data:
{json.dumps(lookup_data, indent=2)}

Enhanced Blueprint Data:
{json.dumps(blueprint, indent=2)}

Please generate a comprehensive markdown document following the agent instructions. Focus on business value and readability for stakeholders."""
        
        return prompt
    
    def _fallback_generation(self, blueprint: dict, lookup_data: dict) -> str:
        """Fallback blueprint generation when Q agent is unavailable"""
        
        app_name = blueprint.get("application_info", {}).get("name", "Unknown Application")
        summary = blueprint.get("summary", {})
        
        # Create basic readable blueprint
        content = f"""# {app_name} - Application Blueprint

## Executive Summary
This Appian application contains {lookup_data.get('total_objects', 0)} objects across multiple component types.

### Component Overview
- **Sites**: {summary.get('sites_count', 0)} user interfaces
- **Record Types**: {summary.get('record_types_count', 0)} data entities
- **Actions**: {summary.get('actions_count', 0)} business operations
- **Process Models**: {summary.get('process_models_count', 0)} automated workflows
- **Data Types**: {summary.get('data_types_count', 0)} custom data structures
- **Integrations**: {summary.get('integrations_count', 0)} external connections
- **Security Groups**: {summary.get('security_groups_count', 0)} access controls

## Object Catalog
The following objects are defined in this application:

"""
        
        # Add object listings by type
        objects_by_type = {}
        for obj in lookup_data.get('objects', []):
            obj_type = obj.get('type', 'Unknown')
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(obj)
        
        for obj_type, objects in objects_by_type.items():
            content += f"### {obj_type}s ({len(objects)})\n\n"
            for obj in objects[:10]:  # Limit to first 10
                content += f"- **{obj.get('name', 'Unnamed')}**: {obj.get('description', 'No description')}\n"
            if len(objects) > 10:
                content += f"- ... and {len(objects) - 10} more\n"
            content += "\n"
        
        content += """
## Notes
This is a basic blueprint generated without Amazon Q agent. For comprehensive business analysis, ensure the Amazon Q agent is properly configured.
"""
        
        # Save fallback blueprint
        output_file = self.blueprint_file.parent / f"{self.blueprint_file.stem.replace('_enhanced_blueprint', '')}_readable_blueprint.md"
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"📝 Fallback blueprint generated: {output_file}")
        return str(output_file)

def main():
    """Main function for testing"""
    if len(sys.argv) != 3:
        print("Usage: python3 blueprint_agent.py <blueprint_file> <lookup_file>")
        sys.exit(1)
    
    agent = AmazonQBlueprintAgent(sys.argv[1], sys.argv[2])
    agent.generate_readable_blueprint()

if __name__ == "__main__":
    main()
