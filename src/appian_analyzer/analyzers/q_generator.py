import json
from ..models import ApplicationBlueprint

class QPromptGenerator:
    """Generates Amazon Q analysis prompts from blueprints"""
    
    def __init__(self, blueprint: ApplicationBlueprint):
        self.blueprint = blueprint
    
    def generate(self) -> str:
        """Generate comprehensive Q analysis prompt"""
        return f"""# Appian Application Blueprint Analysis

## Executive Summary
**Application:** {self.blueprint.name}
**Type:** {self.blueprint.app_type.value}
**Complexity:** {self.blueprint.complexity.value}
**Maintainability:** {self.blueprint.maintainability_score}

{self.blueprint.description}

## Key Metrics
- **Total Components:** {self.blueprint.total_objects}
- **Data Types:** {len(self.blueprint.data_types)}
- **Process Models:** {len(self.blueprint.process_models)}
- **Integrations:** {len(self.blueprint.integrations)}
- **Security Groups:** {len(self.blueprint.security_groups)}

## Analysis Request

Please provide a comprehensive architectural analysis covering:

### 1. Data Architecture Deep Dive
{self._generate_data_analysis_request()}

### 2. Business Process Analysis
{self._generate_process_analysis_request()}

### 3. Integration Architecture Review
{self._generate_integration_analysis_request()}

### 4. Security Framework Assessment
{self._generate_security_analysis_request()}

### 5. Performance & Scalability Considerations
Based on the complexity level ({self.blueprint.complexity.value}) and component distribution, provide recommendations for:
- Performance optimization strategies
- Scalability planning
- Resource allocation guidelines

### 6. Maintenance & Governance Strategy
Given the maintainability score ({self.blueprint.maintainability_score}), recommend:
- Development best practices
- Code organization strategies
- Long-term maintenance approach

## Priority Recommendations
{self._format_recommendations()}

## Detailed Component Data

### Data Types Summary
{self._generate_data_types_summary()}

### Process Models Summary
{self._generate_process_summary()}

### Integration Points Summary
{self._generate_integration_summary()}

### Security Groups Summary
{self._generate_security_summary()}

---

Please provide actionable insights and specific recommendations for each analysis area, focusing on optimization opportunities and best practices for this {self.blueprint.app_type.value.lower()} application.
"""
    
    def _generate_data_analysis_request(self) -> str:
        """Generate data architecture analysis request"""
        if not self.blueprint.data_types:
            return "No custom data types found. Analyze standard Appian data usage patterns."
        
        domains = {}
        for dt in self.blueprint.data_types:
            domain = dt.business_domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(dt.name)
        
        request = f"Analyze {len(self.blueprint.data_types)} custom data types across {len(domains)} business domains:\n"
        
        for domain, types in domains.items():
            request += f"- **{domain}:** {len(types)} types\n"
        
        request += "\nFocus on:\n"
        request += "- Data model optimization opportunities\n"
        request += "- Relationship complexity and potential circular dependencies\n"
        request += "- Domain-driven design improvements\n"
        
        return request
    
    def _generate_process_analysis_request(self) -> str:
        """Generate process analysis request"""
        if not self.blueprint.process_models:
            return "No process models found. This appears to be a data-centric application."
        
        automation_levels = {}
        for pm in self.blueprint.process_models:
            level = pm.automation_level
            automation_levels[level] = automation_levels.get(level, 0) + 1
        
        request = f"Analyze {len(self.blueprint.process_models)} business processes:\n"
        
        for level, count in automation_levels.items():
            request += f"- **{level}:** {count} processes\n"
        
        request += "\nProvide recommendations for:\n"
        request += "- Process optimization and automation opportunities\n"
        request += "- Workflow efficiency improvements\n"
        request += "- Business rule consolidation\n"
        
        return request
    
    def _generate_integration_analysis_request(self) -> str:
        """Generate integration analysis request"""
        if not self.blueprint.integrations:
            return "No external integrations found. Analyze internal data flow patterns."
        
        patterns = {}
        for integration in self.blueprint.integrations:
            pattern = integration.pattern
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        request = f"Analyze {len(self.blueprint.integrations)} integration points:\n"
        
        for pattern, count in patterns.items():
            request += f"- **{pattern}:** {count} integrations\n"
        
        request += "\nEvaluate:\n"
        request += "- Integration architecture patterns and consistency\n"
        request += "- Security implications and best practices\n"
        request += "- Performance and reliability considerations\n"
        
        return request
    
    def _generate_security_analysis_request(self) -> str:
        """Generate security analysis request"""
        if not self.blueprint.security_groups:
            return "No security groups found. Analyze default security patterns."
        
        group_types = {}
        for sg in self.blueprint.security_groups:
            group_type = sg.type
            group_types[group_type] = group_types.get(group_type, 0) + 1
        
        request = f"Analyze {len(self.blueprint.security_groups)} security groups:\n"
        
        for group_type, count in group_types.items():
            request += f"- **{group_type}:** {count} groups\n"
        
        request += "\nReview:\n"
        request += "- Role-based access control effectiveness\n"
        request += "- Security group consolidation opportunities\n"
        request += "- Compliance and governance alignment\n"
        
        return request
    
    def _format_recommendations(self) -> str:
        """Format priority recommendations"""
        if not self.blueprint.recommendations:
            return "No specific recommendations generated."
        
        formatted = ""
        for i, rec in enumerate(self.blueprint.recommendations, 1):
            formatted += f"{i}. {rec}\n"
        
        return formatted
    
    def _generate_data_types_summary(self) -> str:
        """Generate data types summary"""
        if not self.blueprint.data_types:
            return "No custom data types defined."
        
        summary = f"Total: {len(self.blueprint.data_types)} custom data types\n\n"
        
        # Group by business domain
        domains = {}
        for dt in self.blueprint.data_types:
            domain = dt.business_domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(dt)
        
        for domain, types in domains.items():
            summary += f"**{domain} Domain ({len(types)} types):**\n"
            for dt in types[:3]:  # Show first 3 types
                summary += f"- {dt.name} ({len(dt.fields)} fields, complexity: {dt.complexity_score})\n"
            if len(types) > 3:
                summary += f"- ... and {len(types) - 3} more\n"
            summary += "\n"
        
        return summary
    
    def _generate_process_summary(self) -> str:
        """Generate process models summary"""
        if not self.blueprint.process_models:
            return "No process models defined."
        
        summary = f"Total: {len(self.blueprint.process_models)} process models\n\n"
        
        for pm in self.blueprint.process_models[:5]:  # Show first 5
            summary += f"**{pm.name}:**\n"
            summary += f"- Nodes: {len(pm.nodes)}, Automation: {pm.automation_level}\n"
            summary += f"- Functions: {', '.join(pm.business_functions)}\n\n"
        
        if len(self.blueprint.process_models) > 5:
            summary += f"... and {len(self.blueprint.process_models) - 5} more process models\n"
        
        return summary
    
    def _generate_integration_summary(self) -> str:
        """Generate integration summary"""
        if not self.blueprint.integrations:
            return "No external integrations defined."
        
        summary = f"Total: {len(self.blueprint.integrations)} integration points\n\n"
        
        for integration in self.blueprint.integrations:
            summary += f"**{integration.name}:**\n"
            summary += f"- Type: {integration.type}, Pattern: {integration.pattern}\n"
            summary += f"- Security: {integration.security_level}\n\n"
        
        return summary
    
    def _generate_security_summary(self) -> str:
        """Generate security groups summary"""
        if not self.blueprint.security_groups:
            return "No security groups defined."
        
        summary = f"Total: {len(self.blueprint.security_groups)} security groups\n\n"
        
        # Group by business function
        functions = {}
        for sg in self.blueprint.security_groups:
            func = sg.business_function
            if func not in functions:
                functions[func] = []
            functions[func].append(sg)
        
        for function, groups in functions.items():
            summary += f"**{function} ({len(groups)} groups):**\n"
            for sg in groups[:3]:  # Show first 3
                summary += f"- {sg.name} ({sg.type})\n"
            if len(groups) > 3:
                summary += f"- ... and {len(groups) - 3} more\n"
            summary += "\n"
        
        return summary
