# -----------------------------------------------------------------------------
# FILE:         run.py
# AUTHOR:       Aiden Kimmerling <apkimmerling@gmail.com>
# CREATED:      10-01-2026
# LAST EDITED:  10-01-2026
# DESCRIPTION:  This script sets up and runs both `correct_urdf.py` and 
#               `stl_to_obj.py`. It has an optional argument for a urdf
#               name. It then runs `stl_to_obj.py` using pipx to import
#               `pymeshlab`. `stl_to_obj.py` is responsible for, as the
#               name suggests, converting all STLs from a folder to OBJ.
#               Then, this script runs `correct_urdf.py`, which corrects
#               parts of the URDF, such as correcting the mesh package.
# USAGE:        python3 scripts/onshape-to-urdf/run.py "optional_urdf_name"
# DEPENDS:      python3
# LICENSE:      Apache 2.0
# -----------------------------------------------------------------------------

import sys
import subprocess

urdf_name = sys.argv[1] if len(sys.argv) > 1 else "test"
urdf_name += "_core.xacro"

script_folder = "scripts/onshape-to-urdf"
convert_folder = f"{script_folder}/urdf_export_contents"
end_folder = "ros2/description/urdf"

print("Converting STL to OBJ")
subprocess.run(["pipx", "run", "--spec", "pymeshlab", "python3",
                f"{script_folder}/stl_to_obj.py", 
                f"{convert_folder}/assets", f"{end_folder}/meshes"])

print("\nCorrecting the URDF")
subprocess.run(["python3", f"{script_folder}/correct_urdf.py",
                f"{convert_folder}/robot.urdf", f"{end_folder}/{urdf_name}"])

print(f"\nDone! \nMeshes are located in {end_folder}/meshes. \nURDF is in {end_folder}/{urdf_name}")
