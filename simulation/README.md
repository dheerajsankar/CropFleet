# Simulation Assets

## Crop-field world (`worlds/crop_field.sdf`)

Gazebo (gz sim) world for the two-drone PX4 SITL swarm demo:

- Green field mesh (`gazebo/models/crop_field`) with the **same size and shape**
  as the planner's field polygon in `research/field.geojson` (~82 m x 89 m,
  local ENU meters, origin at the first polygon vertex).
- World spherical coordinates match `config/sitl_home.env`, so PX4 local NED
  coordinates line up 1:1 with the field mesh and the planner's mission frame.
- Brown ground plane, sun, and the standard PX4 gz sensor/system plugins.

Launch everything with `./launch_sitl.sh` from the repo root (two PX4 x500
instances, MicroXRCEAgent, and the ROS2 planner stack).

## Regenerating the field mesh

If `research/field.geojson` changes, regenerate the mesh (pure stdlib, no
dependencies):

```bash
python3 simulation/scripts/generate_field_world.py
```
