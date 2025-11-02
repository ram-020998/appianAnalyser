from ..models import ApplicationBlueprint, ComplexityLevel, ApplicationType

class BlueprintAnalyzer:
    """Analyzes and enhances application blueprints with insights"""
    
    def __init__(self, blueprint: ApplicationBlueprint):
        self.blueprint = blueprint
        self.analysis_data = {}
    
    def analyze(self):
        """Perform comprehensive analysis"""
        self._determine_application_type()
        self._calculate_complexity()
        self._assess_maintainability()
        self._generate_recommendations()
        self._calculate_metrics()
    
    def _determine_application_type(self):
        """Determine the primary application type based on enhanced analysis"""
        # Use analysis data if available
        data_model = self.analysis_data.get("data_model", {})
        sites_data = self.analysis_data.get("sites", {})
        actions_data = self.analysis_data.get("actions", {})
        standalone_data = self.analysis_data.get("standalone_objects", {})
        
        # Calculate scores based on comprehensive analysis
        data_score = len(data_model.get("data_entities", [])) * 2
        process_score = standalone_data.get("processes", 0) * 3
        interface_score = standalone_data.get("interfaces", 0)
        integration_score = len(self.blueprint.integrations) * 2
        site_score = len(sites_data.get("sites", [])) * 5
        
        total_score = data_score + process_score + interface_score + integration_score + site_score
        
        if total_score == 0:
            self.blueprint.app_type = ApplicationType.HYBRID
            return
        
        # Determine type based on dominant components
        if process_score > total_score * 0.4:
            self.blueprint.app_type = ApplicationType.PROCESS_CENTRIC
        elif data_score > total_score * 0.5:
            self.blueprint.app_type = ApplicationType.DATA_CENTRIC
        elif integration_score > total_score * 0.3 or interface_score > total_score * 0.4:
            self.blueprint.app_type = ApplicationType.PORTAL
        else:
            self.blueprint.app_type = ApplicationType.HYBRID
    
    def _calculate_complexity(self):
        """Calculate overall application complexity using enhanced data"""
        complexity_score = 0
        
        # Data complexity from enhanced analysis
        data_model = self.analysis_data.get("data_model", {})
        complexity_score += len(data_model.get("data_entities", [])) * 2
        complexity_score += len(data_model.get("relationships", [])) * 1
        
        # Process and interface complexity
        standalone_data = self.analysis_data.get("standalone_objects", {})
        complexity_score += standalone_data.get("processes", 0) * 5
        complexity_score += standalone_data.get("interfaces", 0) * 1
        
        # Integration complexity
        complexity_score += len(self.blueprint.integrations) * 3
        
        # Security complexity
        complexity_score += len(self.blueprint.security_groups)
        
        # Site complexity
        sites_data = self.analysis_data.get("sites", {})
        navigation = sites_data.get("navigation_structure", {})
        complexity_score += navigation.get("total_pages", 0) * 2
        
        # Determine complexity level
        if complexity_score > 2000:
            self.blueprint.complexity = ComplexityLevel.VERY_HIGH
        elif complexity_score > 1000:
            self.blueprint.complexity = ComplexityLevel.HIGH
        elif complexity_score > 500:
            self.blueprint.complexity = ComplexityLevel.MEDIUM
        else:
            self.blueprint.complexity = ComplexityLevel.LOW
    
    def _assess_maintainability(self):
        """Assess application maintainability using enhanced analysis"""
        factors = []
        
        # Data model maintainability
        data_model = self.analysis_data.get("data_model", {})
        if len(data_model.get("data_entities", [])) > 100:
            factors.append("Complex data model")
        
        if len(data_model.get("duplicates", [])) > 0:
            factors.append("Duplicate data entities detected")
        
        # Process maintainability
        standalone_data = self.analysis_data.get("standalone_objects", {})
        if standalone_data.get("processes", 0) > 50:
            factors.append("Many process models")
        
        # Interface maintainability
        if standalone_data.get("interfaces", 0) > 100:
            factors.append("Large number of interfaces")
        
        # Integration maintainability
        if len(self.blueprint.integrations) > 10:
            factors.append("Complex integration landscape")
        
        # Security maintainability
        if len(self.blueprint.security_groups) > 50:
            factors.append("Complex security model")
        
        # Navigation maintainability
        sites_data = self.analysis_data.get("sites", {})
        navigation = sites_data.get("navigation_structure", {})
        if navigation.get("total_pages", 0) > 30:
            factors.append("Complex navigation structure")
        
        # Determine maintainability score
        if len(factors) >= 4:
            self.blueprint.maintainability_score = "Challenging"
        elif len(factors) >= 3:
            self.blueprint.maintainability_score = "Moderate"
        elif len(factors) >= 1:
            self.blueprint.maintainability_score = "Good"
        else:
            self.blueprint.maintainability_score = "Excellent"
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on enhanced analysis"""
        recommendations = []
        
        data_model = self.analysis_data.get("data_model", {})
        
        # Data model recommendations
        if len(data_model.get("data_entities", [])) > 100:
            recommendations.append(
                "Consider data model consolidation - high number of data entities detected"
            )
        
        duplicates = data_model.get("duplicates", [])
        if duplicates:
            recommendations.append(
                f"Found {len(duplicates)} duplicate entities - consolidate CDTs and Record Types"
            )
        
        # CDT migration recommendations
        cdts = data_model.get("cdts", [])
        records = data_model.get("record_types", [])
        if len(cdts) > 0 and len(records) == 0:
            recommendations.append(
                "Consider migrating CDTs to Record Types for modern Appian features"
            )
        
        # Process recommendations
        standalone_data = self.analysis_data.get("standalone_objects", {})
        if standalone_data.get("processes", 0) > 50:
            recommendations.append(
                "Large number of process models - review for consolidation opportunities"
            )
        
        # Integration recommendations
        if len(self.blueprint.integrations) > 10:
            recommendations.append(
                "Implement integration governance framework for better management"
            )
        
        # Security recommendations
        if len(self.blueprint.security_groups) > 50:
            recommendations.append(
                "Review security group structure for consolidation opportunities"
            )
        
        # Performance recommendations
        if self.blueprint.complexity in [ComplexityLevel.HIGH, ComplexityLevel.VERY_HIGH]:
            recommendations.append(
                "Consider performance optimization due to high application complexity"
            )
        
        # Navigation recommendations
        sites_data = self.analysis_data.get("sites", {})
        if not sites_data.get("sites", []):
            recommendations.append(
                "No site objects found - consider implementing proper navigation structure"
            )
        
        self.blueprint.recommendations = recommendations
    
    def _calculate_metrics(self):
        """Calculate additional metrics using enhanced data"""
        # Count total objects from enhanced analysis
        data_model = self.analysis_data.get("data_model", {})
        standalone_data = self.analysis_data.get("standalone_objects", {})
        sites_data = self.analysis_data.get("sites", {})
        
        self.blueprint.total_objects = (
            len(data_model.get("data_entities", [])) +
            standalone_data.get("processes", 0) +
            standalone_data.get("interfaces", 0) +
            len(self.blueprint.integrations) +
            len(self.blueprint.security_groups) +
            len(sites_data.get("sites", []))
        )
