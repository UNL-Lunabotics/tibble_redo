#ifndef TIBBLE_HARDWARE_INFO
#define TIBBLE_HARDWARE_INFO

#include <cmath>

namespace tibble_hardware_info
{
    constexpr double kTwoPi = 2.0 * M_PI;

    struct Rotary {
        double gear_ratio;      // motor revs per joint rev
        double encoder_cpr;     // counts per motor rev (0 if N/A)
        int    direction;       // +1 / -1
        // joint rad/s -> motor rev/s
        constexpr double joint_vel_to_motor_rps(double w) const { return direction * w / kTwoPi * gear_ratio; }
        constexpr double motor_rps_to_joint_vel(double r) const { return direction * r * kTwoPi / gear_ratio; }
    };

    struct Linear {
        double motor_revs_per_m;   // get from specs
        int    direction;
        constexpr double joint_vel_to_motor_rps(double v) const { return direction * v * motor_revs_per_m; }
        constexpr double motor_rps_to_joint_vel(double r) const { return direction * r / motor_revs_per_m; }
    };

    constexpr Rotary DriveLeft  {/*gear*/ 0.0, /*cpr*/ 0.0, +1};
    constexpr Rotary DriveRight {0.0, 0.0, -1};
    constexpr Linear LinearAct  {0.0};
    constexpr Rotary Excavation {0.0, 0.0, +1};

} // namespace tibble_hardware_info

#endif // TIBBLE_HARDWARE_INFO
