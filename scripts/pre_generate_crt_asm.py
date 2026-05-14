Import("env")

from pathlib import Path
import subprocess
import sys


def _is_truthy(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


# Only run for custom IDF environments that need generated sdkconfig/IDF artifacts.
if not _is_truthy(env.GetProjectOption("custom_idf_build", "false")):
    Return()

project_dir = Path(env.subst("$PROJECT_DIR"))
build_dir = Path(env.subst("$BUILD_DIR"))
packages_dir = Path(env.subst("$PROJECT_PACKAGES_DIR"))

certs_dir = project_dir / "managed_components" / "espressif__esp_rainmaker" / "server_certs"
cmake_script = (
    packages_dir
    / "framework-espidf"
    / "tools"
    / "cmake"
    / "scripts"
    / "data_file_embed_asm.cmake"
)

if not certs_dir.is_dir() or not cmake_script.is_file():
    # Nothing to do when RainMaker component is not present yet.
    Return()

cert_files = [
    "rmaker_mqtt_server.crt",
    "rmaker_claim_service_server.crt",
    "rmaker_ota_server.crt",
]

build_dir.mkdir(parents=True, exist_ok=True)

for cert_name in cert_files:
    data_file = certs_dir / cert_name
    source_file = build_dir / f"{cert_name}.S"

    if not data_file.is_file():
        print(f"[pre_generate_crt_asm] Missing cert: {data_file}", file=sys.stderr)
        continue

    cmd = [
        "cmake",
        f"-D DATA_FILE={data_file}",
        f"-D SOURCE_FILE={source_file}",
        "-D FILE_TYPE=TEXT",
        "-P",
        str(cmake_script),
    ]
    subprocess.check_call(cmd)
    print(f"[pre_generate_crt_asm] Generated {source_file}")
