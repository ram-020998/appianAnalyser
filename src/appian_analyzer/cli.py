#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from .core import AppianAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Analyze Appian applications and generate Amazon Q blueprints")
    
    parser.add_argument("zip_file", help="Path to Appian application zip file")
    parser.add_argument("-o", "--output", help="Output file prefix")
    parser.add_argument("--no-prompt", action="store_true", help="Skip Amazon Q prompt generation")
    parser.add_argument("--no-q-analysis", action="store_true", help="Skip comprehensive Q agent analysis")
    
    args = parser.parse_args()
    
    zip_path = Path(args.zip_file)
    if not zip_path.exists():
        print(f"❌ Error: Zip file not found: {zip_path}")
        sys.exit(1)
    
    if not zip_path.suffix.lower() == '.zip':
        print("❌ Error: File must be a .zip file")
        sys.exit(1)
    
    try:
        analyzer = AppianAnalyzer(str(zip_path))
        blueprint = analyzer.analyze()
        
        output_prefix = args.output or zip_path.stem
        
        blueprint_file = analyzer.save_blueprint(f"{output_prefix}_blueprint.json")
        
        if not args.no_prompt:
            prompt_file = analyzer.generate_q_prompt(f"{output_prefix}_q_prompt.txt")
        
        # Q Agent Analysis (default behavior)
        q_analysis_file = None
        if not args.no_q_analysis:
            print("🤖 Running Amazon Q comprehensive analysis...")
            try:
                # Import Q agent service
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from services.q_agent_service import QAgentService
                
                q_service = QAgentService()
                q_analysis_path = f"output/{output_prefix}_q_analysis.md"
                
                result = q_service.analyze_blueprint(blueprint_file, q_analysis_path)
                
                if result["success"]:
                    q_analysis_file = q_analysis_path
                    print("✅ Amazon Q analysis completed successfully!")
                else:
                    print(f"⚠️  Amazon Q analysis failed: {result['error']}")
                    print("📋 Falling back to basic blueprint analysis")
                    
            except ImportError:
                print("⚠️  Q Agent service not available - install required dependencies")
            except Exception as e:
                print(f"⚠️  Q Agent analysis failed: {str(e)}")
                print("📋 Falling back to basic blueprint analysis")
        
        print(f"\n🎯 Analysis Summary:")
        print(f"  📱 Application: {blueprint.name}")
        print(f"  📊 Type: {blueprint.app_type.value}")
        print(f"  📈 Complexity: {blueprint.complexity.value}")
        print(f"  🔧 Maintainability: {blueprint.maintainability_score}")
        print(f"  📋 Components: {blueprint.total_objects}")
        print(f"  💡 Recommendations: {len(blueprint.recommendations)}")
        
        print(f"\n📁 Output Files:")
        print(f"  📊 Blueprint: {blueprint_file}")
        if not args.no_prompt:
            print(f"  📝 Q Prompt: {prompt_file}")
        if q_analysis_file:
            print(f"  🤖 Q Analysis: {q_analysis_file}")
        
        if blueprint.recommendations:
            print(f"\n🎯 Key Recommendations:")
            for i, rec in enumerate(blueprint.recommendations[:3], 1):
                print(f"  {i}. {rec}")
            if len(blueprint.recommendations) > 3:
                print(f"  ... and {len(blueprint.recommendations) - 3} more (see full report)")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
