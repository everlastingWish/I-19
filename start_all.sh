SESSION_NAME="bot_services"

# --- 1. Check if the session already exists and create it if not ---
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    echo "Creating new tmux session: $SESSION_NAME"
    # Create the session and name the first window 'Lavalink'
    tmux new-session -d -s $SESSION_NAME -n Lavalink

    # --- 2. Start Lavalink in the first window (Lavalink) ---
    # The command runs your existing script.
    tmux send-keys -t $SESSION_NAME:Lavalink './lavalink_start.sh' C-m

    # --- 3. Create a new window for ComfyUI and start it ---
    tmux new-window -t $SESSION_NAME -n ComfyUI
    # The command runs your existing script.
    tmux send-keys -t $SESSION_NAME:ComfyUI './comfy_start.sh' C-m

    # --- 4. Create a new window for the Discord Bot and start it ---
    # NOTE: The bot starts immediately after, assuming Lavalink and ComfyUI
    # start fast enough to accept connections.
    tmux new-window -t $SESSION_NAME -n DiscordBot
    tmux send-keys -t $SESSION_NAME:DiscordBot './wait_and_start.sh' C-m

    echo "Services started! You can now detach with Ctrl+b, d or run 'tmux detach'."
    echo "Re-attach anytime with 'tmux attach -t $SESSION_NAME'."
else
    echo "Session $SESSION_NAME is already running."
    echo "Run 'tmux attach -t $SESSION_NAME' to view services."
fi

# --- 5. Optional: Attach to the session immediately ---
tmux attach -t $SESSION_NAME