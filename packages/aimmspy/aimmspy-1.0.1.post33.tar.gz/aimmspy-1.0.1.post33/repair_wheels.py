import subprocess
import site
import os

excluded_so_files = [
    "libarrow_python.so.2000",
    "libarrow.so.2000",
    "libarrow_substrait.so.2000",
    "libarrow_dataset.so.2000",
    "libarrow_acero.so.2000",
    "libparquet.so.2000"
]

def repair_wheels_in_folder(folder_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # create the exclude arguments for auditwheel
    exclude_args = []
    for so_file in excluded_so_files:
        exclude_args.append("--exclude")
        exclude_args.append(so_file)
        
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".whl"):
            wheel_path = os.path.join(folder_path, filename)

            print(f"Repairing: {wheel_path}")
            cmd_args = ["auditwheel", "repair", *exclude_args, "-w", output_folder, wheel_path]
            print("Command:", " ".join(cmd_args))
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"Successfully repaired: {filename}")
            else:
                print(f"Failed to repair: {filename}")
                print("stderr:", result.stderr)

# on linux only:
if os.name != 'posix':
    print("This script is intended to run on Linux systems only.")
    exit(0)

# add pyarrow to the LD_LIBRARY_PATH, such that auditwheel can find it for verifying the wheels
os.environ["LD_LIBRARY_PATH"] = f"{site.getsitepackages()[0]}/pyarrow:" + os.environ.get("LD_LIBRARY_PATH", "")

# Check if auditwheel is installed
try:
    subprocess.run(["auditwheel", "--version"], check=True)
except FileNotFoundError:
    print("auditwheel is not installed.")
    exit(1)

wheel_folder = os.path.join(os.getcwd(), "dist")
repair_wheels_in_folder(wheel_folder, wheel_folder)

# remove the original wheels
for filename in os.listdir(wheel_folder):
    # if filename contains "-linux_" and ends with ".whl" remove it
    if "-linux_" in filename and filename.endswith(".whl"):
        os.remove(os.path.join(wheel_folder, filename))
        print(f"Removed original wheel: {filename}")

