"""
Create a sample Excel file for testing the Email Agent
"""

import pandas as pd

# Sample data for testing
sample_data = [
    {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'company_name': 'Tech Innovations Inc.',
        'position': 'Software Developer',
        'department': 'Engineering',
        'start_date': '2024-01-15'
    },
    {
        'name': 'Jane Smith',
        'email': 'jane.smith@example.com',
        'company_name': 'Design Studios Ltd.',
        'position': 'UI/UX Designer',
        'department': 'Design',
        'start_date': '2024-01-22'
    },
    {
        'name': 'Mike Johnson',
        'email': 'mike.johnson@example.com',
        'company_name': 'Data Analytics Corp.',
        'position': 'Data Scientist',
        'department': 'Analytics',
        'start_date': '2024-02-01'
    },
    {
        'name': 'Sarah Wilson',
        'email': 'sarah.wilson@example.com',
        'company_name': 'Marketing Solutions',
        'position': 'Marketing Manager',
        'department': 'Marketing',
        'start_date': '2024-02-15'
    },
    {
        'name': 'David Brown',
        'email': 'david.brown@example.com',
        'company_name': 'Finance First',
        'position': 'Financial Analyst',
        'department': 'Finance',
        'start_date': '2024-03-01'
    }
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel file
output_file = 'sample_recipients.xlsx'
df.to_excel(output_file, index=False)

print(f"✅ Sample Excel file created: {output_file}")
print(f"📊 Contains {len(df)} sample recipients")
print(f"📋 Columns: {', '.join(df.columns.tolist())}")
print("\n📝 You can use this file to test the Email Agent:")
print("   1. Upload this file in the web interface")
print("   2. Use placeholders like {name}, {company_name}, {position}")
print("   3. Test with sample email requests")

# Display preview
print(f"\n📋 Sample data preview:")
print(df.head().to_string(index=False))
