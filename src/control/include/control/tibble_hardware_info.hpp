#ifndef TIBBLE_HARDWARE_INFO
#define TIBBLE_HARDWARE_INFO

#include <cmath>

namespace tibble_hardware_info {
constexpr double kTwoPi = 2.0 * M_PI;
constexpr double deg2rad(double d) { return d * M_PI / 180.0; }

struct Rotary {
  double gear_ratio;  // motor revs per joint rev
  double encoder_cpr; // counts per motor rev (0 if N/A)
  int direction;      // +1 / -1
  // joint rad/s -> motor rev/s
  constexpr double joint_vel_to_motor_rps(double w) const {
    return direction * w / kTwoPi * gear_ratio;
  }
  constexpr double motor_rps_to_joint_vel(double r) const {
    return direction * r * kTwoPi / gear_ratio;
  }
};

struct Linear {
  double motor_revs_per_m; // get from specs
  int direction;
  constexpr double joint_vel_to_motor_rps(double v) const {
    return direction * v * motor_revs_per_m;
  }
  constexpr double motor_rps_to_joint_vel(double r) const {
    return direction * r / motor_revs_per_m;
  }
};

// Position based servo
// NOTE: for servos, "pulses" are basically equivalent to position values,
// so anytime you see pulses, you can replace that with position to help it make
// more sense
struct PwmServo {
  double pulse_min_us;  // pulse at one end of travel
  double pulse_max_us;  // pulse at the other end
  double range_rad;     // total travel from min to max
  double zero_pulse_us; // starting/default pulse (position when urdf = 0)
  int direction;        // +1 / -1 (set either here or in the URDF, not both)

  constexpr double rad_per_us() const {
    return range_rad / (pulse_max_us - pulse_min_us);
  }

  // URDF joint angle (rad) -> pulse width (us), clamped to the servo's range
  constexpr double joint_to_pulse_us(double joint_rad) const {
    const double us = zero_pulse_us + direction * joint_rad / rad_per_us();
    return std::clamp(us, pulse_min_us, pulse_max_us);
  }

  // Pulse width -> joint angle. Last commanded angle, not measured
  constexpr double pulse_us_to_joint(double us) const {
    return direction * (us - zero_pulse_us) * rad_per_us();
  }
};

} // namespace tibble_hardware_info

#endif // TIBBLE_HARDWARE_INFO
