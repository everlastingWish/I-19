LAVALINK_PORT=2333 
COMFYUI_PORT=8188 
BOT_COMMAND="python3 mainNEW.py" 
VENV_ACTIVATE_SCRIPT="./venv/bin/activate"
# You'll need to know the correct ports for your setup

echo "Waiting for Lavalink server on port $LAVALINK_PORT..."
# Wait for Lavalink port
while ! nc -z localhost $LAVALINK_PORT 2>/dev/null; do
    sleep 5
done
echo "Lavalink server is UP!"

echo "Waiting for ComfyUI server on port $COMFYUI_PORT..."
# Wait for ComfyUI port
while ! nc -z localhost $COMFYUI_PORT 2>/dev/null; do
    sleep 5
done
echo "ComfyUI server is UP!"

# --- VENV ACTIVATION ---
if [ -f "$VENV_ACTIVATE_SCRIPT" ]; then
    # Use 'source' to run the activation script in the current shell
    source "$VENV_ACTIVATE_SCRIPT"
    echo "Virtual environment activated."
else
    echo "ERROR: VENV activation script not found at $VENV_ACTIVATE_SCRIPT"
    exit 1
fi
# --- END VENV ACTIVATION ---

echo "All dependencies started. Launching Discord Bot..."
# Start the Discord Bot
exec $BOT_COMMAND

# NOTE: 'nc' (netcat) must be installed for this to work.
# On most Linux distributions, you can install it with:
# sudo apt install netcat -y