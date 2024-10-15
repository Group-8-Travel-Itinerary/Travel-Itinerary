import subprocess
import sys
import os
import platform

def update_requirements():
    try:
        # Get the current working directory
        cwd = os.getcwd()

        # Check if pipreqs is installed; if not, install it without --user
        subprocess.run([sys.executable, "-m", "pip", "install", "pipreqs"], check=True)

        # Construct the pipreqs command
        pipreqs_command = [
            "pipreqs", cwd, "--force", "--ignore", "venv"
        ]

        # Run pipreqs to generate/update requirements.txt
        subprocess.run(pipreqs_command, check=True)
        
        print("requirements.txt has been updated successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running pipreqs: {e}")
    except FileNotFoundError:
        print("pipreqs is not installed. Please install pipreqs first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    update_requirements()

