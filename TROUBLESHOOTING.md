# Troubleshooting

## `ModuleNotFoundError: No module named 'audio'` (or any backend module)

Python is running from the wrong directory. Make sure you run from the `backend/` folder:

```bash
cd backend && ../.venv/bin/python main.py
```

Or just use `npm start` which handles this automatically.

---

## `npm start` fails / Python exits immediately

The venv probably isn't set up. Run the setup script from the repo root:

```bash
./setup.sh
```

Then try `npm start` again.

---

## `ModuleNotFoundError: No module named 'pkg_resources'`

This affects Python 3.12+ where `pkg_resources` was removed. The `setup.sh` script patches this automatically, but if you set up manually:

```bash
python -c "
import site
path = site.getsitepackages()[0] + '/webrtcvad.py'
content = open(path).read()
content = content.replace('import pkg_resources\n\n', '')
content = content.replace(\"__version__ = pkg_resources.get_distribution('webrtcvad').version\", '__version__ = \"2.0.10\"')
open(path, 'w').write(content)
print('patched')
"
```

Run this from inside the venv:

```bash
backend/.venv/bin/python -c "..."
```

---

## `pip install` fails with `externally-managed-environment` (Arch Linux)

Don't install system-wide. Use the venv:

```bash
python -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
```

---

## No audio / nothing being transcribed

1. Check your audio device. For meeting audio (loopback), set `AUDIO_DEVICE` in `backend/config.py` to your monitor source:
   ```bash
   pactl list sources short  # find the line ending in .monitor
   ```
2. If using mic, leave `AUDIO_DEVICE = None`
3. Run the mic test to verify STT is working:
   ```bash
   cd backend && ../.venv/bin/python test_mic.py
   ```

---

## Gemini API errors

Make sure your API key is set:

```bash
export GEMINI_API_KEY=your_key_here
```

Add to `~/.zshrc` or `~/.bashrc` to make it permanent.

---

## Overlay doesn't appear

The overlay is always running but starts transparent. It only shows content once audio is being received and transcribed. Check the terminal for `[python]` stderr output to see if the backend is running correctly.
