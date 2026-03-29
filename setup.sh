#!/bin/bash
set -e

echo "Setting up Python venv..."
python3 -m venv backend/.venv
backend/.venv/bin/pip install -q -r backend/requirements.txt

echo "Installing Node dependencies..."
npm install

echo ""
echo "Done."
echo ""
echo "Next steps:"
echo "  1. Create a .env file in the project root:"
echo "     echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env"
echo ""
echo "  2. For system audio capture (recommended), install BlackHole:"
echo "     brew install blackhole-2ch"
echo "     Then log out and back in, and set up a Multi-Output Device in Audio MIDI Setup."
echo "     See README.md for full instructions."
echo ""
echo "  3. Run: npm start"
