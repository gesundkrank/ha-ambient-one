#!/bin/bash
# Setup GitHub repository for Ambient One integration

echo "=========================================="
echo "Ambient One - GitHub Setup"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo ""
fi

# Check for .gitignore
if [ ! -f .gitignore ]; then
    echo "⚠️  No .gitignore found, using existing one"
fi

# Add files
echo "📝 Staging files..."
git add .
echo ""

# Show status
echo "📊 Git status:"
git status --short
echo ""

# Create initial commit
echo "💾 Creating initial commit..."
read -p "Press Enter to commit with default message (or Ctrl+C to cancel)"
git commit -m "Initial commit: Ambient One Home Assistant integration

Features:
- Complete API client for Supabase backend
- Config flow UI setup
- 13+ sensor entities per device
- Air quality platform support
- Real-time updates every 60 seconds
- Battery and WiFi signal monitoring
- Full documentation and testing guides"
echo ""

echo "✅ Git repository initialized!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Create GitHub repository:"
echo "   → Go to https://github.com/new"
echo "   → Repository name: ha-ambient-one"
echo "   → Description: Home Assistant integration for Ambient One air quality sensor"
echo "   → Make it public (for HACS)"
echo "   → Don't initialize with README (we already have one)"
echo ""
echo "2. Push to GitHub:"
echo "   → Copy the commands from GitHub and run them"
echo "   → Or run:"
echo "     git remote add origin https://github.com/gesundkrank/ha-ambient-one.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "3. Enable GitHub features:"
echo "   → Go to repository Settings → General"
echo "   → Enable Issues and Discussions"
echo ""
echo "4. Create a release:"
echo "   → Go to Releases → Create a new release"
echo "   → Tag: v1.0.0"
echo "   → Title: Initial Release"
echo "   → Publish release"
echo ""
echo "5. Install via HACS:"
echo "   → In Home Assistant: HACS → Integrations"
echo "   → Click ⋮ → Custom repositories"
echo "   → Add: https://github.com/gesundkrank/ha-ambient-one"
echo "   → Category: Integration"
echo ""
echo "=========================================="
