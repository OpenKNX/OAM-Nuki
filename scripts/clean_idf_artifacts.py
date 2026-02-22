"""
Open ■
┬────┴  clean_idf_artifacts
■ KNX   2026 OpenKNX - Erkan Çolak

PlatformIO extra_script: clean_idf_artifacts.py
Removes IDF-generated artifacts when `pio run --target clean` is executed.
"""
Import("env")
import os
import shutil

if not env.GetOption("clean"):
    Return()  # Only active during --target clean

PROJECT_DIR = env.subst("$PROJECT_DIR")
BUILD_DIR   = env.subst("$BUILD_DIR")
ENV_NAME    = env.subst("$PIOENV")

extra_clean = [
    os.path.join(PROJECT_DIR, "sdkconfig.defaults"),
    os.path.join(PROJECT_DIR, f"sdkconfig.{ENV_NAME}"),
    os.path.join(PROJECT_DIR, "managed_components"),
    os.path.join(PROJECT_DIR, ".dummy"),
    os.path.join(PROJECT_DIR, "dependencies.lock"),
    os.path.join(PROJECT_DIR, "CMakeLists.txt"),
    
]

print(f"\n[clean_idf] Cleaning IDF artifacts for '{ENV_NAME}' ...")
for path in extra_clean:
    if os.path.exists(path):
        print(f"[clean_idf]  Deleting: {os.path.relpath(path, PROJECT_DIR)}")
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
    else:
        print(f"[clean_idf]  (not found): {os.path.relpath(path, PROJECT_DIR)}")
print("[clean_idf] Done.\n")
