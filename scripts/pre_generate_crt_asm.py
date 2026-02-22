"""
Open ■
┬────┴  pre_generate_crt_asm
■ KNX   2026 OpenKNX - Erkan Çolak

PlatformIO pre-script:
1. Generates .S assembly files for target_add_binary_data() entries from managed_components/.
   - Cert/binary source files are stored in components/certs/ (committed to git).
   - .incbin ALWAYS points to components/certs/<file> -- always available, no cache needed.
   - managed_components/ present: update components/certs/ + generate .S files.
   - managed_components/ missing (after clean): use components/certs/ directly.
   - No auto-rebuild, no temporary cache needed.
2. Patches CCFLAGS globally with -Wno-discarded-qualifiers if rainmaker certs are present.
"""

import os
import re
import shutil

Import("env")  # noqa: F821

# During clean runs do nothing -- clean_idf_artifacts.py handles cleanup
if env.GetOption("clean"):
    Return()

build_dir    = env.subst("$BUILD_DIR")
project_dir  = env.subst("$PROJECT_DIR")
managed_dir  = os.path.join(project_dir, "managed_components")

# components/certs/ is committed to git -- always available, survives everything
certs_dir    = os.path.join(project_dir, "components", "certs")

# Build dir may not exist yet on the very first build
os.makedirs(build_dir, exist_ok=True)
os.makedirs(certs_dir, exist_ok=True)


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
binary_data_pattern = re.compile(
    r'target_add_binary_data\s*\(\s*\S+\s+"([^"]+)"\s+(TEXT|BINARY)\s*\)',
    re.MULTILINE,
)


def _symbol_name(filepath):
    safe = re.sub(r"[^a-zA-Z0-9]", "_", os.path.basename(filepath))
    return "_binary_" + safe


def _write_asm(incbin_path, dest_s, file_type="TEXT"):
    """Generate a .S assembly file; incbin_path points to components/certs/<file>."""
    var = _symbol_name(incbin_path)
    os.makedirs(os.path.dirname(dest_s), exist_ok=True)
    with open(dest_s, "w") as f:
        f.write("    .section .rodata\n")
        f.write(f"    .global {var}_start\n")
        f.write(f"    .global {var}_end\n")
        f.write(f"{var}_start:\n")
        f.write(f'    .incbin "{incbin_path}"\n')
        f.write(f"{var}_end:\n")
        if file_type == "TEXT":
            f.write(".byte 0\n")


# --------------------------------------------------------------------------- #
# Known entries file -- persists filename:type mappings alongside the certs
# --------------------------------------------------------------------------- #
KNOWN_ENTRIES_FILE = os.path.join(certs_dir, ".known_entries")


def _load_known_entries():
    entries = {}
    if os.path.isfile(KNOWN_ENTRIES_FILE):
        with open(KNOWN_ENTRIES_FILE) as f:
            for line in f:
                line = line.strip()
                if line and ":" in line:
                    name, ftype = line.split(":", 1)
                    entries[name.strip()] = ftype.strip()
    return entries


def _save_known_entries(entries):
    with open(KNOWN_ENTRIES_FILE, "w") as f:
        for name, ftype in sorted(entries.items()):
            f.write(f"{name}:{ftype}\n")


# --------------------------------------------------------------------------- #
# 1) managed_components/ present -> update components/certs/, generate .S files
# --------------------------------------------------------------------------- #
if os.path.isdir(managed_dir):
    known_entries = _load_known_entries()

    for root, _dirs, files in os.walk(managed_dir):
        if "CMakeLists.txt" not in files:
            continue
        cml_path = os.path.join(root, "CMakeLists.txt")
        try:
            with open(cml_path, encoding="utf-8") as fh:
                cmake_content = fh.read()
        except OSError:
            continue

        for m in binary_data_pattern.finditer(cmake_content):
            rel_path  = m.group(1)
            file_type = m.group(2)

            if rel_path.startswith("${"):
                print(f"[pre_generate] Skipping cmake variable path: {rel_path}")
                continue

            src_file = os.path.abspath(os.path.join(root, rel_path))
            if not os.path.isfile(src_file):
                print(f"[pre_generate] WARNING: not found: {src_file}")
                continue

            fname      = os.path.basename(src_file)
            cert_file  = os.path.join(certs_dir, fname)

            # Update components/certs/ from managed_components/ (commit if changed)
            shutil.copy2(src_file, cert_file)
            known_entries[fname] = file_type

            # Generate .S file (.incbin -> components/certs/<file>)
            s_name = fname + ".S"
            dest_s = os.path.join(build_dir, s_name)
            if not os.path.isfile(dest_s):
                print(f"[pre_generate] Generating: {s_name}")
                _write_asm(cert_file, dest_s, file_type)
            else:
                print(f"[pre_generate] Already exists: {s_name}")

    _save_known_entries(known_entries)

# --------------------------------------------------------------------------- #
# 2) managed_components/ missing (after pio clean) -> use components/certs/
# --------------------------------------------------------------------------- #
else:
    known_entries = _load_known_entries()
    if not known_entries:
        print("[pre_generate] WARNING: components/certs/.known_entries is empty or missing.")
        print("[pre_generate]   Run a build once with managed_components/ present to populate it.")
    else:
        for fname, file_type in known_entries.items():
            cert_file = os.path.join(certs_dir, fname)
            if not os.path.isfile(cert_file):
                print(f"[pre_generate] WARNING: {fname} not found in components/certs/ -- skipping")
                continue
            s_name = fname + ".S"
            dest_s = os.path.join(build_dir, s_name)
            if not os.path.isfile(dest_s):
                print(f"[pre_generate] Generating (from components/certs/): {s_name}")
                _write_asm(cert_file, dest_s, file_type)
            else:
                print(f"[pre_generate] Already exists: {s_name}")


# --------------------------------------------------------------------------- #
# 3) Add -Wno-discarded-qualifiers globally if rainmaker certs are present
#    in components/certs/ (they are committed, so this is always true).
# --------------------------------------------------------------------------- #
RAINMAKER_CERT = os.path.join(certs_dir, "rmaker_mqtt_server.crt")

if os.path.isfile(RAINMAKER_CERT):
    if "-Wno-discarded-qualifiers" not in str(env.get("CFLAGS", [])):
        env.Append(CFLAGS=["-Wno-discarded-qualifiers"])
    if "-Wno-error=discarded-qualifiers" not in str(env.get("CXXFLAGS", [])):
        env.Append(CXXFLAGS=["-Wno-error=discarded-qualifiers"])
    print("[pre_generate] Fixed const-qualifier flags for espressif__esp_rainmaker")
