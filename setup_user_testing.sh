#!/bin/bash
# OpenAGI User Testing System Setup Script

echo "🤖 OpenAGI User Testing System Setup"
echo "===================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $python_version == *"3."* ]]; then
    echo "✅ Python 3 detected: $python_version"
else
    echo "❌ Python 3 required but not found"
    exit 1
fi

# Create data directories
echo "Creating data directories..."
mkdir -p beta_testing_data
mkdir -p recruitment_data
echo "✅ Data directories created"

# Install required Python packages (if in virtual environment)
echo "Checking for virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    echo "Installing required packages..."
    pip install dataclasses json csv datetime pathlib > /dev/null 2>&1
    echo "✅ Required packages installed"
else
    echo "⚠️  No virtual environment detected. Consider activating one."
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x tools/beta_tester_manager.py
chmod +x tools/recruitment_automation.py
echo "✅ Scripts are now executable"

# Test the tools
echo "Testing beta tester manager..."
python3 tools/beta_tester_manager.py --action stats > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Beta tester manager working correctly"
else
    echo "❌ Beta tester manager test failed"
fi

echo "Testing recruitment automation..."
python3 tools/recruitment_automation.py --action targets > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Recruitment automation working correctly"
else
    echo "❌ Recruitment automation test failed"
fi

# Create sample data
echo "Creating sample data..."
python3 tools/beta_tester_manager.py --action sample > /dev/null 2>&1
echo "✅ Sample data created"

echo ""
echo "🎉 Setup complete! Your user testing system is ready."
echo ""
echo "Quick start commands:"
echo "1. View application stats:     python3 tools/beta_tester_manager.py --action stats"
echo "2. Generate recruitment report: python3 tools/beta_tester_manager.py --action report"
echo "3. View recruitment targets:   python3 tools/recruitment_automation.py --action targets"
echo "4. Generate message template:  python3 tools/recruitment_automation.py --action template --template linkedin_outreach"
echo ""
echo "Next steps:"
echo "1. Read USER_TESTING.md for comprehensive guide"
echo "2. Review tools/templates.md for recruitment materials"
echo "3. Set up your Discord server and Google Forms"
echo "4. Start your first recruitment campaign!"
echo ""
echo "For help, contact: beta-testing@viiicorp.com"