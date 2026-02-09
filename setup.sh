#!/bin/bash
# Setup script for PR Message Generator

echo "=========================================="
echo "PR Message Generator - Setup"
echo "=========================================="
echo ""

# Check if config.json exists
if [ ! -f "pr_agent/config.json" ]; then
    echo "📝 Creating config.json from template..."
    cp pr_agent/config.json.example pr_agent/config.json
    echo "✅ config.json created"
else
    echo "ℹ️  config.json already exists"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Run Web UI: streamlit run pr_agent/app.py"
echo "   or CLI: python pr_agent/main.py pr --input 'your changes'"
echo ""
