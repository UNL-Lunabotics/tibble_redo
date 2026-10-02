#ifndef TIBBLE_CONTROLLER_HPP
#define TIBBLE_CONTROLLER_HPP

#include <atomic>
#include <string>
#include <unordered_map>
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
#include "geometry_msgs/msg/twist_stamped.hpp"

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
        
        // YAML parameters (that aren't interface related)
        std::string cmd_topic_;
        std::string odom_topic_;
        std::string tf_topic_;
        double wheel_radius_;               // meters
        double wheel_separation_;           // meters
        double paddle_speed_;               // radians/second
        double la_speed_;                   // meters/second
        double excav_dt_speed_multiplier_;
        long int telemetry_update_rate_;         // milliseconds

        rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr cmd_vel_sub_;

        realtime_tools::RealtimeBuffer<geometry_msgs::msg::TwistStamped> twist_cmd_buffer_;
    };
} // namespace tibble_controller

#endif // TIBBLE_CONTROLLER_HPP