# app.py

import threading
from scheduler import schedule_tasks

# Main entry point for the app
if __name__ == '__main__':
    # Run the scheduler in a separate thread so it doesn't block the main app
    scheduler_thread = threading.Thread(target=schedule_tasks, daemon=True)
    scheduler_thread.start()

    # Keep the app running
    while True:
        pass  # Keep the app alive to allow background scheduling
