#!/bin/bash
# Fix opencv: deepface pulls opencv-python which needs libGL.so.1 (not in container).
# Replace with headless version that provides the same cv2 without GUI deps.
# Use the venv pip — the app runs from /code/.venv/
/code/.venv/bin/pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null
/code/.venv/bin/pip install --force-reinstall --no-deps opencv-python-headless==4.13.0.92
