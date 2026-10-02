# -----------------------------------------------------------------------------
# FILE:         correct_urdf.py
# AUTHOR:       Aiden Kimmerling <apkimmerling@gmail.com>
# CREATED:      10-01-2026
# LAST EDITED:  10-01-2026
# DESCRIPTION:  This script modifies a URDF that comes from onshape-to-robot. It
#               removes the `base_link`, removes the robot `name`, corrects the
#               package name, and replaces all `.stl` to `.obj`. It can be used
#               standalone, or with the accompanying `run.py` script.
#               It will modify the URDF from `start_path` and save it as a new file
#               at the `end_path` location.
# USAGE:        python3 scripts/onshape-to-urdf/correct_urdf.py "/path/to/onshape/urdf" "/path/to/new/urdf"
# DEPENDS:      python3
# LICENSE:      Apache 2.0
# -----------------------------------------------------------------------------

import sys
import re

start_path = sys.argv[1]
end_path = sys.argv[2]

# 1. Read the contents of the file
with open(start_path, "r", encoding="utf-8") as file:
    file_contents = file.read()

# 2. Make the replacements
updated_contents = re.sub(r'<robot name=".*?">', "<robot>", file_contents)

updated_contents = re.sub(
    r'\s*<!--\s*(?:Link\s+)?base_link\s*-->\s*<link name="base_link">.*?</link>',
    "",
    updated_contents,
    flags=re.DOTALL
)

updated_contents = updated_contents.replace("package://assets", "package://description/urdf/meshes")

updated_contents = updated_contents.replace(".stl", ".obj")

# 3. Write the updated contents back to the file
with open(end_path, "w", encoding="utf-8") as file:
    file.write(updated_contents)
