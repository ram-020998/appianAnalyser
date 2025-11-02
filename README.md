# Appian Application Analyzer

A professional Python tool for analyzing Appian application zip files and generating detailed blueprints optimized for Amazon Q analysis.

## Features

- **🏗️ Professional OOP Architecture**: Clean, maintainable code structure
- **📊 Enhanced Accuracy**: Improved parsing with detailed component analysis
- **🎯 Smart Classification**: Automatic categorization of components by business domain
- **📈 Complexity Analysis**: Sophisticated scoring and maintainability assessment
- **🔍 Deep Insights**: Process automation levels, security patterns, integration analysis
- **🤖 Q-Ready Output**: Structured prompts optimized for Amazon Q consumption

## Quick Start

```bash
# Analyze an Appian application
python3 analyze_appian.py applicationZips/RequirementsManagementv2.3.0.zip

# This generates:
# - RequirementsManagementv2.3.0_blueprint.json (detailed analysis)
# - RequirementsManagementv2.3.0_q_prompt.txt (Q-ready prompt)
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd appianAnalyser

# Install dependencies (optional - uses only standard library by default)
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## What Gets Analyzed

### 1. Data Architecture (Enhanced)
- **149 Custom Data Types** with field-level analysis
- **Business Domain Classification** (Requirements Management, Audit, etc.)
- **Relationship Mapping** and complexity scoring
- **Circular Dependency Detection**

### 2. Business Processes (New)
- **196 Process Models** with node-level analysis
- **Automation Level Assessment** (Manual, Partial, Highly Automated)
- **Business Function Mapping**
- **Complexity Scoring** based on node types and patterns

### 3. Integration Architecture (Enhanced)
- **14 Integration Points** with pattern classification
- **Security Level Assessment** (High, Medium, Low)
- **Endpoint Analysis** and protocol detection
- **Connected Systems vs Web APIs** differentiation

### 4. Security Model (Enhanced)
- **134 Security Groups** with type classification
- **Business Function Mapping**
- **Role-Based Access Analysis**
- **Consolidation Opportunities**

### 5. Application Intelligence
- **Application Type Detection** (Process-Centric, Data-Centric, Hybrid, Portal)
- **Complexity Assessment** (Low, Medium, High, Very High)
- **Maintainability Scoring** (Excellent, Good, Moderate, Challenging)
- **Actionable Recommendations**

## Project Structure

```
appianAnalyser/
├── src/appian_analyzer/           # Main package
│   ├── models/                    # Data models
│   ├── parsers/                   # Component parsers
│   │   ├── datatype_parser.py     # XSD/Data type parsing
│   │   ├── process_parser.py      # Process model parsing
│   │   ├── integration_parser.py  # Connected systems & APIs
│   │   └── security_parser.py     # Security groups
│   ├── analyzers/                 # Analysis engines
│   │   ├── blueprint_analyzer.py  # Blueprint enhancement
│   │   └── q_generator.py         # Q prompt generation
│   ├── core.py                    # Main analyzer class
│   └── cli.py                     # Command line interface
├── analyze_appian.py              # Simple runner script
├── applicationZips/               # Input zip files
└── tests/                         # Test suite
```

## Analysis Results Example

For the Requirements Management application:

```
🎯 Analysis Summary:
  📱 Application: AS RM Full Application
  📊 Type: Process-Centric
  📈 Complexity: Very High
  🔧 Maintainability: Challenging
  📋 Components: 493
  💡 Recommendations: 4

🎯 Key Recommendations:
  1. Consider data model consolidation - high number of custom data types detected
  2. Implement integration governance framework for better management
  3. Review security group structure for consolidation opportunities
  4. Consider performance optimization due to high application complexity
```

## Output Files

### Enhanced Blueprint JSON
Comprehensive structured analysis including:
- Executive summary with intelligent metrics
- Component-wise detailed breakdown
- Business domain classifications
- Complexity and maintainability assessments
- Actionable recommendations

### Intelligent Q Prompt
Amazon Q-optimized prompt featuring:
- Executive summary with key insights
- Domain-specific analysis requests
- Component summaries with business context
- Priority recommendations
- Structured data for deep analysis

## Integration with Amazon Q

The generated prompt provides Amazon Q with:

1. **Contextual Understanding**: Business domains and application type
2. **Focused Analysis Areas**: Based on actual component distribution
3. **Priority Recommendations**: Data-driven insights
4. **Structured Queries**: Optimized for comprehensive responses

## Advanced Usage

```bash
# Custom output naming
python3 analyze_appian.py app.zip -o custom_name

# Skip Q prompt generation
python3 analyze_appian.py app.zip --no-prompt

# Use as Python package
from appian_analyzer import AppianAnalyzer
analyzer = AppianAnalyzer("app.zip")
blueprint = analyzer.analyze()
```

## Requirements

- Python 3.7+
- Standard library (no external dependencies for basic usage)
- Optional: lxml for enhanced XML parsing

## Key Improvements

✅ **Professional OOP Design**: Clean separation of concerns
✅ **Enhanced Accuracy**: Better parsing and classification
✅ **Intelligent Analysis**: Smart categorization and scoring
✅ **Comprehensive Coverage**: All major Appian components
✅ **Actionable Insights**: Data-driven recommendations
✅ **Q Integration**: Optimized for Amazon Q analysis

This tool transforms raw Appian exports into intelligent architectural documentation, enabling better decision-making for development, maintenance, and optimization strategies.
