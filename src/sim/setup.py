from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "config"), glob("config/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        # `*.*` means all files/folders with any name/extension
        (os.path.join("share", package_name, "worlds"), glob("worlds/*.sdf")),
        (os.path.join("share", package_name, "worlds"), glob("worlds/*.mjcf")),
        (os.path.join("share", package_name, "worlds", "meshes"), glob("worlds/meshes/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena"), glob("worlds/meshes/artemis_arena/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "arena_columns"), glob("worlds/meshes/artemis_arena/arena_columns/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "arena_pipe"), glob("worlds/meshes/artemis_arena/arena_pipe/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "arena_walls"), glob("worlds/meshes/artemis_arena/arena_walls/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "arena_window_frames"), glob("worlds/meshes/artemis_arena/arena_window_frames/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "arena_windows"), glob("worlds/meshes/artemis_arena/arena_windows/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "column"), glob("worlds/meshes/artemis_arena/column/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "lunar_surface"), glob("worlds/meshes/artemis_arena/lunar_surface/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "artemis_arena", "lunar_surface2"), glob("worlds/meshes/artemis_arena/lunar_surface2/*.*")),

        (os.path.join("share", package_name, "worlds", "meshes", "core"), glob("worlds/meshes/core/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "core", "rock_rough"), glob("worlds/meshes/core/rock_rough/*.*")),

        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena"), glob("worlds/meshes/ucf_arena/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena", "arena_barriers"), glob("worlds/meshes/ucf_arena/arena_barriers/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena", "arena_rods"), glob("worlds/meshes/ucf_arena/arena_rods/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena", "arena_walls"), glob("worlds/meshes/ucf_arena/arena_walls/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena", "arena_windows"), glob("worlds/meshes/ucf_arena/arena_windows/*.*")),
        (os.path.join("share", package_name, "worlds", "meshes", "ucf_arena", "lunar_surface_better"), glob("worlds/meshes/ucf_arena/lunar_surface_better/*.*")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
