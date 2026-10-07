std_msgs/Header header

# MODE_DISABLED: controller must command zero on everything
# MODE_MANUAL:    fields below come from a human input device.
# MODE_AUTONOMY:  commands come from Nav2
uint8 MODE_DISABLED=0
uint8 MODE_MANUAL=1
uint8 MODE_AUTONOMY=2
uint8 mode

float64 linear_x   # m/s
float64 angular_z  # rad/s

float64 drum_cmd  # -1 to 1, sign = direction, magnitude = speed fraction
float64 la_cmd    # -1 to 1, +1 = extend, -1 = retract

# Current desired state of these two things (closed/open, off/on)
bool latch
bool vibe

bool panic
