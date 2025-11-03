# Appian Application Analyzer

A professional Python tool for analyzing Appian application zip files and generating detailed technical blueprints.

## Features

- **🏗️ Professional OOP Architecture**: Clean, maintainable code structure
- **📊 Enhanced Accuracy**: Improved parsing with detailed component analysis
- **🎯 Smart Classification**: Automatic categorization of components by business domain
- **📈 Complexity Analysis**: Sophisticated scoring and maintainability assessment
- **🔍 Deep Insights**: Process automation levels, security patterns, integration analysis
- **📋 Object Lookup**: Complete UUID-to-name mapping for all objects

## Quick Start

```bash
# Analyze an Appian application using module
python3 -m src.appian_analyzer applicationZips/RequirementsManagementv2.3.0.zip

# Or install and use as command
pip install -e .
appian-analyzer applicationZips/RequirementsManagementv2.3.0.zip

# This generates in output/ folder:
# - RequirementsManagementv2.3.0_blueprint.json (detailed technical analysis)
# - RequirementsManagementv2.3.0_object_lookup.json (UUID-to-name mapping)
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

### 1. Data Architecture
- **Record Types** with field-level analysis and relationships
- **Data Types (CDTs)** with complete metadata
- **Business Domain Classification**
- **Relationship Mapping** and complexity scoring

### 2. Business Processes
- **Process Models** with node-level analysis
- **Automation Level Assessment**
- **Business Function Mapping**
- **Complexity Scoring** based on node types and patterns

### 3. Integration Architecture
- **Connected Systems** with pattern classification
- **Web APIs** and endpoint analysis
- **Security Level Assessment**
- **Integration Point Classification**

### 4. Security Model
- **Security Groups** with type classification
- **Business Function Mapping**
- **Role-Based Access Analysis**

### 5. User Interface
- **Sites** with page hierarchy analysis
- **Interfaces** with component mapping
- **Expression Rules** for business logic
- **Constants** for configuration management

### 6. Application Intelligence
- **Application Type Detection**
- **Complexity Assessment** (Low, Medium, High, Very High)
- **Maintainability Scoring**
- **Actionable Recommendations**

## Project Structure

```
appianAnalyser/
├── src/appian_analyzer/           # Main package
│   └── enhanced_core.py           # Enhanced analyzer with object lookup
├── analyze_simple.py              # Simple CLI runner
├── applicationZips/               # Input zip files
├── output/                        # Generated output files
├── schemas/                       # XML schema documentation
└── tests/                         # Test suite
```

## Analysis Results Example

For the Requirements Management application:

```
🎯 Analysis Summary:
  📱 Application: RequirementsManagementv2.3.0
  📊 Complexity: Very High
  📋 Total Objects: 3,172
  💡 Recommendations: 2

🎯 Component Breakdown:
  • Sites: 2
  • Record Types: 110
  • Process Models: 196
  • Interfaces: 582
  • Expression Rules: 1,271
  • Security Groups: 132
  • Constants: 702
  • Integrations: 5
```

## Output Files

### Technical Blueprint JSON
Comprehensive structured analysis including:
- Executive summary with intelligent metrics
- Component-wise detailed breakdown
- Business domain classifications
- Complexity and maintainability assessments
- Actionable recommendations

### Object Lookup JSON
Complete UUID-to-name mapping for:
- Easy object reference resolution
- Cross-component relationship tracking
- Development and maintenance support

## Advanced Usage

```bash
# Analyze any Appian application zip using module
python3 -m src.appian_analyzer path/to/your/application.zip

# Or use as Python package
from appian_analyzer import AppianAnalyzer
analyzer = AppianAnalyzer("app.zip")
result = analyzer.analyze()
blueprint = result["blueprint"]
object_lookup = result["object_lookup"]

# Output files will be generated in output/ folder
ls output/
```

## Requirements

- Python 3.7+
- Standard library (no external dependencies for basic usage)

## Key Improvements

✅ **Professional OOP Design**: Clean separation of concerns  
✅ **Enhanced Accuracy**: Better parsing and classification  
✅ **Intelligent Analysis**: Smart categorization and scoring  
✅ **Comprehensive Coverage**: All major Appian components  
✅ **Actionable Insights**: Data-driven recommendations  
✅ **Object Lookup**: Complete UUID-to-name mapping  

This tool transforms raw Appian exports into intelligent architectural documentation, enabling better decision-making for development, maintenance, and optimization strategies.
