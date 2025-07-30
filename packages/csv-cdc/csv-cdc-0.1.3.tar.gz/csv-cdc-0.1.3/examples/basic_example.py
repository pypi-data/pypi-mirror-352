from csvcdc import CSVCDC, OutputFormatter
import os

def create_sample_data():
    """Create sample CSV files for demonstration"""
    
    # Create base.csv
    base_data = """id,name,price,category
1,Widget,10.99,Tools
2,Gadget,25.50,Electronics  
3,Book,15.99,Education
4,Lamp,45.00,Home
"""
    
    # Create delta.csv  
    delta_data = """id,name,price,category
1,Widget,12.99,Tools
2,Gadget,25.50,Electronics
4,Lamp,39.99,Home
5,Phone,299.99,Electronics
"""
    
    os.makedirs('sample_data', exist_ok=True)
    
    with open('sample_data/base.csv', 'w') as f:
        f.write(base_data)
        
    with open('sample_data/delta.csv', 'w') as f:
        f.write(delta_data)
    
    print("✅ Sample data created in sample_data/ directory")

def basic_comparison():
    """Basic file comparison example"""
    print("\n" + "="*50)
    print("BASIC COMPARISON EXAMPLE")
    print("="*50)
    
    # Create CDC instance with default settings
    cdc = CSVCDC(primary_key=[0])  # Use first column as primary key
    
    # Compare files
    result = cdc.compare('sample_data/base.csv', 'sample_data/delta.csv')
    
    # Print summary
    print(f"📊 Comparison Summary:")
    print(f"   Additions: {len(result.additions)}")
    print(f"   Modifications: {len(result.modifications)}")
    print(f"   Deletions: {len(result.deletions)}")
    
    # Show detailed results
    print(f"\n📝 Detailed Results:")
    output = OutputFormatter.format_diff(result)
    print(output)

def json_output_example():
    """Example showing JSON output format"""
    print("\n" + "="*50)
    print("JSON OUTPUT EXAMPLE")
    print("="*50)
    
    cdc = CSVCDC(primary_key=[0])
    result = cdc.compare('sample_data/base.csv', 'sample_data/delta.csv')
    
    # Format as JSON
    json_output = OutputFormatter.format_json(result)
    print(json_output)
    
    # Save to file
    with open('sample_data/changes.json', 'w') as f:
        f.write(json_output)
    print(f"\n💾 JSON output saved to sample_data/changes.json")

def column_selection_example():
    """Example showing column selection"""
    print("\n" + "="*50)
    print("COLUMN SELECTION EXAMPLE")
    print("="*50)
    
    # Compare only name and price columns (ignore category)
    cdc = CSVCDC(
        primary_key=[0],
        ignore_columns=[3]  # Ignore category column
    )
    
    result = cdc.compare('sample_data/base.csv', 'sample_data/delta.csv')
    
    print("Comparing only ID, Name, and Price (ignoring Category):")
    output = OutputFormatter.format_diff(result)
    print(output)

if __name__ == '__main__':
    print("🚀 CSV CDC Basic Examples")
    
    # Create sample data
    create_sample_data()
    
    # Run examples
    basic_comparison()
    json_output_example()
    column_selection_example()
    
    print(f"\n✨ Examples completed! Check the sample_data/ directory for generated files.")