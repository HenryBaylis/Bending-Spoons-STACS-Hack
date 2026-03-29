#!/bin/bash
set -e

echo "Setting up Python venv..."
python3 -m venv backend/.venv
backend/.venv/bin/pip install -q -r backend/requirements.txt

# Fix webrtcvad's use of pkg_resources which is unavailable in Python 3.12+
WEBRTCVAD=$(backend/.venv/bin/python -c "import site; print(site.getsitepackages()[0])")/webrtcvad.py
if grep -q "pkg_resources" "$WEBRTCVAD" 2>/dev/null; then
  echo "Patching webrtcvad for Python 3.12+..."
  python3 -c "
content = open('$WEBRTCVAD').read()
content = content.replace('import pkg_resources\n\n', '')
content = content.replace(\"__version__ = pkg_resources.get_distribution('webrtcvad').version\", '__version__ = \"2.0.10\"')
open('$WEBRTCVAD', 'w').write(content)
"
fi

echo "Installing Node dependencies..."
npm install

echo "Done. Run 'npm start' to launch."
