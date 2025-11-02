"""
Q Agent Service for Appian Analyzer - Handle Amazon Q CLI agent interactions
"""
import subprocess
import json
import os
from pathlib import Path


class QAgentService:
    """Handle Q CLI agent operations for Appian analysis"""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path(__file__).parent.parent

    def analyze_blueprint(self, blueprint_path: str, output_path: str = None) -> dict:
        """Analyze Appian blueprint using Q agent"""
        try:
            # Read the blueprint file
            with open(blueprint_path, 'r') as f:
                blueprint_data = json.load(f)

            # Create analysis prompt
            prompt = self._create_analysis_prompt(blueprint_data)

            # Execute Q agent
            result = self._execute_q_agent("appian-analyzer", prompt)

            if result.returncode == 0:
                # Save analysis to file if output path provided
                if output_path:
                    self._save_analysis(result.stdout, output_path)
                
                return {
                    "success": True,
                    "analysis": result.stdout,
                    "output_file": output_path
                }
            else:
                return {
                    "success": False,
                    "error": f"Q agent failed with return code: {result.returncode}",
                    "stderr": result.stderr
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }

    def _create_analysis_prompt(self, blueprint_data: dict) -> str:
        """Create analysis prompt from blueprint data"""
        app_info = blueprint_data.get('application_info', {})
        app_name = app_info.get('name', 'Unknown Application')
        
        prompt = f"""# Appian Application Blueprint Analysis

## Application Overview
**Name:** {app_name}
**Type:** {app_info.get('type', 'Unknown')}
**Complexity:** {app_info.get('complexity', 'Unknown')}
**Maintainability:** {app_info.get('maintainability', 'Unknown')}

## Component Summary
- **Total Components:** {app_info.get('total_objects', 0)}
- **Data Types:** {blueprint_data.get('data_architecture', {}).get('total_types', 0)}
- **Process Models:** {blueprint_data.get('business_processes', {}).get('total_processes', 0)}
- **Integrations:** {len(blueprint_data.get('integrations', {}).get('integration_points', []))}
- **Security Groups:** {len(blueprint_data.get('security_model', {}).get('security_groups', []))}

## Integration Details
"""
        
        # Add integration details
        integrations = blueprint_data.get('integrations', {}).get('integration_points', [])
        if integrations:
            for integration in integrations:
                prompt += f"- **{integration.get('name', 'Unknown')}:** {integration.get('type', 'Unknown')} (Security: {integration.get('security_level', 'Unknown')})\n"
        
        prompt += f"""

## Security Groups Breakdown
"""
        
        # Add security group details
        security_groups = blueprint_data.get('security_model', {}).get('security_groups', [])
        if security_groups:
            # Group by type
            group_types = {}
            for group in security_groups:
                group_type = group.get('type', 'Unknown')
                if group_type not in group_types:
                    group_types[group_type] = 0
                group_types[group_type] += 1
            
            for group_type, count in group_types.items():
                prompt += f"- **{group_type}:** {count} groups\n"

        prompt += """

Please provide a comprehensive architectural analysis covering:

1. **Critical Security Issues** - Identify immediate risks and remediation steps
2. **Integration Architecture Review** - Assess patterns, security, and performance
3. **Security Framework Assessment** - Consolidation opportunities and governance
4. **Performance Optimization** - Scalability and maintainability improvements
5. **Priority Action Plan** - Immediate, short-term, and long-term recommendations

Focus on actionable insights with specific timelines and business impact."""

        return prompt

    def _execute_q_agent(self, agent_name: str, prompt: str) -> subprocess.CompletedProcess:
        """Execute Q CLI agent with prompt"""
        cmd = ['q', 'chat', '--agent', agent_name, '--no-interactive', prompt]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.base_dir),
            timeout=120  # 2 minutes timeout for complex analysis
        )
        
        return result

    def _save_analysis(self, analysis_content: str, output_path: str):
        """Save analysis to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(analysis_content)
