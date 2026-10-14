#ifndef TIBBLE_CONTROLLER_HPP
#define TIBBLE_CONTROLLER_HPP

#include <string>
#include <vector>

#include "controller_interface/controller_interface.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/duration.hpp"
#include "rclcpp/subscription.hpp"
#include "rclcpp/time.hpp"
#include "rclcpp/timer.hpp"
#include "rclcpp_lifecycle/lifecycle_publisher.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "realtime_tools/realtime_buffer.hpp"
#include "rclcpp/qos.hpp"
#include "rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp"
#include "interfaces/msg/tibble_command.hpp"

namespace tibble_controller
{
    class TibbleController : public controller_interface::ControllerInterface
    {
    public:
        TibbleController() = default;

        controller_interface::InterfaceConfiguration command_interface_configuration() const override;

        controller_interface::InterfaceConfiguration state_interface_configuration() const override;

        controller_interface::return_type update(
            const rclcpp::Time &time, const rclcpp::Duration &period) override;

        controller_interface::CallbackReturn on_init() override;

        controller_interface::CallbackReturn on_configure(
            const rclcpp_lifecycle::State &previous_state) override;

        controller_interface::CallbackReturn on_activate(
            const rclcpp_lifecycle::State &previous_state) override;

        controller_interface::CallbackReturn on_deactivate(
            const rclcpp_lifecycle::State &previous_state) override;

    private:
        // Interface setup
        std::vector<std::string> joint_names_;
        std::vector<std::string> command_interface_types_;
        std::vector<std::string> state_interface_types_;

        std::vector<std::reference_wrapper<hardware_interface::LoanedCommandInterface>>
            joint_position_command_interface_;
        std::vector<std::reference_wrapper<hardware_interface::LoanedCommandInterface>>
            joint_velocity_command_interface_;
        std::vector<std::reference_wrapper<hardware_interface::LoanedStateInterface>>
            joint_position_state_interface_;
        std::vector<std::reference_wrapper<hardware_interface::LoanedStateInterface>>
            joint_velocity_state_interface_;

        std::unordered_map<
            std::string, std::vector<std::reference_wrapper<hardware_interface::LoanedCommandInterface>> *>
            command_interface_map_ = {
                {"position", &joint_position_command_interface_},
                {"velocity", &joint_velocity_command_interface_}};

        std::unordered_map<
            std::string, std::vector<std::reference_wrapper<hardware_interface::LoanedStateInterface>> *>
            state_interface_map_ = {
                {"position", &joint_position_state_interface_},
                {"velocity", &joint_velocity_state_interface_}};

        // NOTE: these indices assume the `joints:` YAML list is, in order:
        // [DL_Rotate, DR_Rotate, LA_Extend, Excavation_Rotate]
        static constexpr std::size_t kDlRotate = 0;
        static constexpr std::size_t kDrRotate = 1;
        static constexpr std::size_t kLaExtend = 2;
        static constexpr std::size_t kExcavationRotate = 3;

        
        // YAML parameters (that aren't interface related)
        std::string cmd_topic_;
        std::string odom_topic_;
        std::string tf_topic_;
        double wheel_radius_;               // meters
        double wheel_separation_;           // meters
        double paddle_speed_;               // radians/second
        double la_speed_;                   // meters/second
        double la_min_;                     // meters
        double la_max_;                     // meters
        double excav_dt_speed_multiplier_;
        double digging_threshold_;
        double cmd_timeout_;                // any commands older than this are put to 0
        long int telemetry_update_rate_;         // milliseconds

        rclcpp::Subscription<interfaces::msg::TibbleCommand>::SharedPtr cmd_sub_;

        realtime_tools::RealtimeBuffer<interfaces::msg::TibbleCommand::SharedPtr> cmd_buffer_;
    };
} // namespace tibble_controller

#endif // TIBBLE_CONTROLLER_HPP