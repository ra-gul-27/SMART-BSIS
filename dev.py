import os
import sys
import time
import subprocess

WATCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
MAIN_SCRIPT = os.path.join(WATCH_DIR, "main.py")

def get_mtimes():
    """Scan all .py files in app/ and return their modification timestamps."""
    mtimes = {}
    for root, dirs, files in os.walk(WATCH_DIR):
        if "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    mtimes[path] = os.path.getmtime(path)
                except OSError:
                    pass
    return mtimes

def main():
    print("=====================================================")
    print(" 🚀 SMART BUS STAND - AUTO-RELOAD DEV RUNNER")
    print(" 👀 Watching 'app/' for any file changes...")
    print(" ✨ Edit any file -> App will auto-restart instantly!")
    print(" 🛑 Press Ctrl+C in this terminal to stop.")
    print("=====================================================\n")

    proc = subprocess.Popen([sys.executable, MAIN_SCRIPT])
    last_mtimes = get_mtimes()

    restarting = False
    try:
        while True:
            time.sleep(0.7)

            # If user manually closed the window, wait for a file save to relaunch
            if proc.poll() is not None and not restarting:
                time.sleep(0.5)
                current_mtimes = get_mtimes()
                if current_mtimes != last_mtimes:
                    last_mtimes = current_mtimes
                    print("\n🔄 Changes detected! Relaunching app...")
                    proc = subprocess.Popen([sys.executable, MAIN_SCRIPT])
                continue

            current_mtimes = get_mtimes()
            if current_mtimes != last_mtimes:
                last_mtimes = current_mtimes
                print("\n🔄 Code change detected! Auto-restarting app...")
                restarting = True
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    proc.kill()
                time.sleep(0.2)
                proc = subprocess.Popen([sys.executable, MAIN_SCRIPT])
                restarting = False
    except KeyboardInterrupt:
        print("\nStopping Auto-Reload Runner...")
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()
