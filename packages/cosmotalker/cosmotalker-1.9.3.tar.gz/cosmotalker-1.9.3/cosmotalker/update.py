import subprocess
import sys

def update():
    packages = [
        "cosmodb",
        "customtkinter",
        "pillow",
        "requests",
        "pyperclip",
        "cosmotalker",
        "sheetsmart"
    ]

    for package_name in packages:
        try:
            # Get current version
            old = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True, text=True
            )
            old_version = "None"
            if old.returncode == 0:
                for line in old.stdout.splitlines():
                    if line.startswith("Version:"):
                        old_version = line.split(":")[1].strip()
                        break
            print(f"\n🔍 Current version of '{package_name}': {old_version}")

            # Uninstall
            print(f"🧹 Uninstalling '{package_name}'...")
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                capture_output=True, text=True
            )

            # Reinstall latest version
            print(f"📦 Reinstalling latest version of '{package_name}'...")
            install = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True, text=True
            )

            # Get new version
            new = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True, text=True
            )
            new_version = "Unknown"
            if new.returncode == 0:
                for line in new.stdout.splitlines():
                    if line.startswith("Version:"):
                        new_version = line.split(":")[1].strip()
                        break

            # Final message
            if install.returncode == 0:
                print(f"\n✅ '{package_name}' updated: {old_version} → {new_version}")
            else:
                print(f"\n❌ Installation failed for '{package_name}':\n{install.stderr}")

            print("\n" + "="*15 + f" Finished: {package_name} " + "="*15 + "\n")

        except Exception as e:
            print(f"\n❗ Error with '{package_name}': {e}")

