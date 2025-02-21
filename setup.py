import sys
from cx_Freeze import setup, Executable

# Build options
build_exe_options = {
    "packages": ["tkinter", "Pillow"],  # Pillow yerine PIL yazılmıştı, düzeltildi.
    "include_files": [
        "program.json",
        "notes_history.txt",
        "board-jolly-clown (1).jpg"
    ]
}

# Platform bazlı GUI ayarı
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Setup işlemi
setup(
    name="program1",
    version="1.0",
    description="Eğitim Programı Takip Uygulaması",
    options={"build_exe": build_exe_options},
    executables=[Executable("program_tracker.py", base=base)]
)
