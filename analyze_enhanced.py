#!/usr/bin/env python3
"""
Enhanced Appian Application Analyzer CLI
Generates both technical JSON and human-readable blueprints
"""

import sys
import json
import os
from datetime import datetime
from src.appian_analyzer.enhanced_core import EnhancedAppianAnalyzer

def generate_human_readable_blueprint(blueprint_data: dict, output_path: str):
    """Generate human-readable blueprint from technical data"""
    
    app_name = blueprint_data["metadata"]["application_name"]
    object_lookup = blueprint_data["object_lookup"]
    
    # Helper function to resolve UUIDs to names
    def resolve_name(uuid: str) -> str:
        if not uuid:
            return "Unknown"
        obj = object_lookup.get(uuid)
        return obj["name"] if obj else f"Unknown ({uuid[:8]}...)"
    
    markdown_content = f"""# {app_name} - Application Blueprint

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

**Application:** {app_name}  
**Total Objects:** {blueprint_data["metadata"]["total_objects"]}  
**Complexity:** {blueprint_data["summary"]["complexity_assessment"]}  

### Component Overview
- **Sites:** {blueprint_data["summary"]["total_sites"]}
- **Record Types:** {blueprint_data["summary"]["total_record_types"]}
- **Process Models:** {blueprint_data["summary"]["total_process_models"]}
- **Interfaces:** {blueprint_data["summary"]["total_interfaces"]}
- **Expression Rules:** {blueprint_data["summary"]["total_rules"]}
- **Data Types:** {blueprint_data["summary"]["total_data_types"]}
- **Integrations:** {blueprint_data["summary"]["total_integrations"]}
- **Security Groups:** {blueprint_data["summary"]["total_security_groups"]}
- **Constants:** {blueprint_data["summary"]["total_constants"]}

## Site Architecture

"""
    
    # Sites section
    for site in blueprint_data["sites"]:
        markdown_content += f"""### {site["name"]}

**Description:** {site["description"] or "No description provided"}

**Pages:**
"""
        for page in site["pages"]:
            markdown_content += f"""
#### {page["name"]}
- **UI Components:** {len(page["ui_objects"])} objects
"""
            for ui_obj in page["ui_objects"]:
                markdown_content += f"  - {ui_obj['name']} ({ui_obj['type']})\n"
            
            if page["visibility"]:
                markdown_content += f"- **Visibility:** {page['visibility']}\n"
    
    # Data Model section
    markdown_content += f"""
## Data Model

The application manages {len(blueprint_data["record_types"])} primary data entities:

"""
    
    for record in blueprint_data["record_types"]:
        markdown_content += f"""### {record["name"]}

**Description:** {record["description"] or "No description provided"}

**Fields:** {len(record["fields"])} fields defined
"""
        for field in record["fields"][:5]:  # Show first 5 fields
            required = " (Required)" if field["required"] else ""
            pk = " (Primary Key)" if field["primary_key"] else ""
            markdown_content += f"- **{field['name']}** ({field['type']}){required}{pk}\n"
        
        if len(record["fields"]) > 5:
            markdown_content += f"- ... and {len(record['fields']) - 5} more fields\n"
        
        if record["relationships"]:
            markdown_content += f"\n**Relationships:**\n"
            for rel in record["relationships"]:
                target_name = resolve_name(rel["target_record"]["uuid"])
                markdown_content += f"- **{rel['name']}** → {target_name}\n"
        
        if record["actions"]:
            markdown_content += f"\n**Available Actions:** {len(record['actions'])} actions\n"
            for action in record["actions"]:
                target_process = action.get("target_process", {})
                target_uuid = target_process.get("uuid") if target_process else None
                process_name = resolve_name(target_uuid) if target_uuid else "Unknown"
                action_title = action.get("title", "Unnamed Action")
                markdown_content += f"- **{action_title}** → {process_name}\n"
        
        markdown_content += "\n"
    
    # Process Automation section
    markdown_content += f"""
## Process Automation

The application includes {len(blueprint_data["process_models"])} automated processes:

"""
    
    for process in blueprint_data["process_models"]:
        markdown_content += f"""### {process["name"]}

**Description:** {process["description"] or "No description provided"}

**Process Variables:** {len(process["variables"])} variables
"""
        for var in process["variables"][:3]:  # Show first 3 variables
            param = " (Parameter)" if var["parameter"] else ""
            markdown_content += f"- **{var['name']}** ({var['type']}){param}\n"
        
        if len(process["variables"]) > 3:
            markdown_content += f"- ... and {len(process['variables']) - 3} more variables\n"
        
        markdown_content += f"\n**Process Flow:** {len(process['nodes'])} nodes, {len(process['flows'])} connections\n"
        
        # Show key nodes
        user_tasks = [n for n in process["nodes"] if n["type"] == "User Input Task"]
        script_tasks = [n for n in process["nodes"] if n["type"] == "Script Task"]
        
        if user_tasks:
            markdown_content += f"- **User Tasks:** {len(user_tasks)} manual steps\n"
        if script_tasks:
            markdown_content += f"- **Automated Tasks:** {len(script_tasks)} automated steps\n"
        
        markdown_content += "\n"
    
    # Integration Architecture section
    if blueprint_data["integrations"]:
        markdown_content += f"""
## Integration Architecture

The application connects to {len(blueprint_data["integrations"])} external systems:

"""
        for integration in blueprint_data["integrations"]:
            markdown_content += f"""### {integration["name"]}

**Type:** {integration["type"]}  
**Description:** {integration["description"] or "No description provided"}

"""
    
    # Security Model section
    markdown_content += f"""
## Security Model

The application defines {len(blueprint_data["security_groups"])} security groups:

"""
    
    # Group by type
    group_types = {}
    for group in blueprint_data["security_groups"]:
        group_type = group["type"]
        if group_type not in group_types:
            group_types[group_type] = []
        group_types[group_type].append(group)
    
    for group_type, groups in group_types.items():
        markdown_content += f"""### {group_type} Groups ({len(groups)} groups)

"""
        for group in groups[:5]:  # Show first 5 groups
            markdown_content += f"- **{group['name']}**"
            if group["description"]:
                markdown_content += f": {group['description']}"
            markdown_content += "\n"
        
        if len(groups) > 5:
            markdown_content += f"- ... and {len(groups) - 5} more groups\n"
        
        markdown_content += "\n"
    
    # Recommendations section
    if blueprint_data["summary"]["recommendations"]:
        markdown_content += f"""
## Recommendations

"""
        for i, rec in enumerate(blueprint_data["summary"]["recommendations"], 1):
            markdown_content += f"{i}. {rec}\n"
    
    # Object Lookup section
    markdown_content += f"""
## Object Lookup Reference

| S.No | Object Name | Type | Description |
|------|-------------|------|-------------|
"""
    
    for uuid, obj in sorted(object_lookup.items(), key=lambda x: x[1]["s_no"]):
        desc = obj["description"][:50] + "..." if len(obj["description"]) > 50 else obj["description"]
        markdown_content += f"| {obj['s_no']} | {obj['name']} | {obj['object_type']} | {desc} |\n"
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_enhanced.py <appian_zip_file>")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    
    if not os.path.exists(zip_path):
        print(f"❌ Error: File {zip_path} not found")
        sys.exit(1)
    
    # Extract base name for output files
    base_name = os.path.basename(zip_path).replace('.zip', '')
    
    try:
        print(f"🚀 Starting Enhanced Analysis of {base_name}")
        print("=" * 60)
        
        # Initialize analyzer
        analyzer = EnhancedAppianAnalyzer(zip_path)
        
        # Perform analysis
        blueprint = analyzer.analyze()
        
        # Generate outputs
        json_output = f"{base_name}_enhanced_blueprint.json"
        markdown_output = f"{base_name}_human_blueprint.md"
        lookup_output = f"{base_name}_object_lookup.json"
        
        print(f"\n📝 Generating output files...")
        
        # Save technical JSON blueprint
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(blueprint, f, indent=2, ensure_ascii=False)
        
        # Save object lookup separately
        with open(lookup_output, 'w', encoding='utf-8') as f:
            json.dump(blueprint["object_lookup"], f, indent=2, ensure_ascii=False)
        
        # Generate human-readable blueprint
        generate_human_readable_blueprint(blueprint, markdown_output)
        
        # Display summary
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Summary:")
        print(f"   • Total Objects: {blueprint['metadata']['total_objects']}")
        print(f"   • Complexity: {blueprint['summary']['complexity_assessment']}")
        print(f"   • Sites: {blueprint['summary']['total_sites']}")
        print(f"   • Record Types: {blueprint['summary']['total_record_types']}")
        print(f"   • Process Models: {blueprint['summary']['total_process_models']}")
        print(f"   • Interfaces: {blueprint['summary']['total_interfaces']}")
        print(f"   • Rules: {blueprint['summary']['total_rules']}")
        print(f"   • Integrations: {blueprint['summary']['total_integrations']}")
        print(f"   • Security Groups: {blueprint['summary']['total_security_groups']}")
        
        print(f"\n📁 Generated Files:")
        print(f"   • {json_output} (Technical JSON)")
        print(f"   • {markdown_output} (Human-readable)")
        print(f"   • {lookup_output} (Object lookup)")
        
        if blueprint['summary']['recommendations']:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(blueprint['summary']['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Close analyzer
        analyzer.close()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
