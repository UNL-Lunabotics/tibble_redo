# -----------------------------------------------------------------------------
# FILE:         stl_to_obj.py
# AUTHOR:       Aiden Kimmerling <apkimmerling@gmail.com>
# CREATED:      10-01-2026
# LAST EDITED:  10-01-2026
# DESCRIPTION:  This script converts all `.stl` from a given folder to `.obj`,
#               using a library called `pymeshlab`. Normally, `pymeshlab` is
#               installed in a virtual environment. To bypass this, pipx can
#               be run in conjunction to this script, which will embed a 
#               `pymeshlab` instance to the script. See USAGE for more information.
#               Can be run standalone or with the accompanying `run.py` script.
#               The resulting `.obj` will be saved to the `end_path`.
# USAGE:        pipx run --spec pymeshlab python3 scripts/onshape-to-urdf/stl_to_obj.py "/path/to/onshape/assets" "/path/to/new/meshes"
# DEPENDS:      python3, pymeshlab, pipx or venv
# LICENSE:      Apache 2.0
# -----------------------------------------------------------------------------

import os
import sys
from pathlib import Path
import pymeshlab

start_path = sys.argv[1]
end_path = sys.argv[2]

# Create the folder if it doesn't exist
Path(end_path).mkdir(parents=True, exist_ok=True)

for filename in os.listdir(start_path):
    if filename.endswith(".STL"):
        # Get files
        stl_path = os.path.join(start_path, filename)
        obj_path = os.path.join(end_path, filename.replace(".STL", ".obj"))
        
        # Convert stl to obj
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(stl_path)

        # `save_vertex_normal=False` ensures flat surfaces
        # stay flat. Otherwise sometimes has a weird curve
        ms.save_current_mesh(obj_path, save_vertex_normal=False)
