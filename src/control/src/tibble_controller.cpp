#include "control/tibble_controller.hpp"

#include <algorithm>
#include <string>
#include <vector>

using config_type = controller_interface::interface_configuration_type;

namespace tibble_controller
{

    controller_interface::CallbackReturn TibbleController::on_init()
    {
        try
        {
            // Declare node parameters. These are lists from the tibble_controller.yaml file into variables declared in header

            // Interface declaration
            joint_names_ = auto_declare<std::vector<std::string>>("joints", joint_names_);
            command_interface_types_ =
                auto_declare<std::vector<std::string>>("command_interfaces", command_interface_types_);
            state_interface_types_ =
                auto_declare<std::vector<std::string>>("state_interfaces", state_interface_types_);
            
            // Configuration declaration
            cmd_topic_ = auto_declare<std::string>("command_topic", cmd_topic_);
            odom_topic_ = auto_declare<std::string>("odometry_topic", odom_topic_);
            tf_topic_ = auto_declare<std::string>("transform_topic", tf_topic_);
            wheel_radius_ = auto_declare<double>("wheel_radius", wheel_radius_);
            wheel_separation_ = auto_declare<double>("wheel_separation", wheel_separation_);
            paddle_speed_ = auto_declare<double>("paddle_speed", paddle_speed_);
            la_speed_ = auto_declare<double>("linear_actuator_speed", la_speed_);
            excav_dt_speed_multiplier_ = auto_declare<double>("excav_dt_speed_multiplier", excav_dt_speed_multiplier_);
            telemetry_update_rate_ = auto_declare<long int>("telemetry_update_rate", telemetry_update_rate_);
        }
        catch (const std::exception &e)
        {
            RCLCPP_ERROR(get_node()->get_logger(), "on_init exception: %s", e.what());
            return controller_interface::CallbackReturn::ERROR;
        }

        RCLCPP_INFO(get_node()->get_logger(), "Initialized TibbleController.");
        return CallbackReturn::SUCCESS;
    }

    controller_interface::InterfaceConfiguration TibbleController::command_interface_configuration() const
    {
        controller_interface::InterfaceConfiguration config = {config_type::INDIVIDUAL, {}};

        config.names.reserve(joint_names_.size() * command_interface_types_.size());
        for (const auto &joint_name : joint_names_)
        {
            for (const auto &interface_type : command_interface_types_)
            {
                config.names.push_back(joint_name + "/" + interface_type);
            }
        }

        return config;
    }

    controller_interface::InterfaceConfiguration TibbleController::state_interface_configuration() const
    {
        controller_interface::InterfaceConfiguration config = {config_type::INDIVIDUAL, {}};

        config.names.reserve(joint_names_.size() * state_interface_types_.size());
        for (const auto &joint_name : joint_names_)
        {
            for (const auto &interface_type : state_interface_types_)
            {
                config.names.push_back(joint_name + "/" + interface_type);
            }
        }

        return config;
    }

    controller_interface::CallbackReturn TibbleController::on_configure(const rclcpp_lifecycle::State &)
    {
        cmd_vel_sub_ = get_node()->create_subscription<geometry_msgs::msg::TwistStamped>(
            "/cmd_vel", rclcpp::SystemDefaultsQoS(),
            [this](const geometry_msgs::msg::TwistStamped::SharedPtr msg)
            {
                twist_cmd_buffer_.writeFromNonRT(*msg);
            });

        // TODO: odom pub, tf broadcaster, state service

        RCLCPP_INFO(get_node()->get_logger(), "Configured TibbleController.");
        return CallbackReturn::SUCCESS;
    }

    controller_interface::CallbackReturn TibbleController::on_activate(const rclcpp_lifecycle::State &)
    {
        // clear out vectors in case of restart
        joint_position_command_interface_.clear();
        joint_velocity_command_interface_.clear();
        joint_position_state_interface_.clear();
        joint_velocity_state_interface_.clear();

        // assign command interfaces
        for (auto &interface : command_interfaces_)
        {
            command_interface_map_[interface.get_interface_name()]->push_back(interface);
        }

        // assign state interfaces
        for (auto &interface : state_interfaces_)
        {
            state_interface_map_[interface.get_interface_name()]->push_back(interface);
        }

        if (command_interfaces_.empty() || state_interfaces_.empty())
        {
            RCLCPP_ERROR(get_node()->get_logger(), "Missing controller interfaces.");
            return controller_interface::CallbackReturn::ERROR;
        }

        RCLCPP_INFO(get_node()->get_logger(), "Activated TibbleController.");
        return CallbackReturn::SUCCESS;
    }

    controller_interface::return_type TibbleController::update(const rclcpp::Time &time, const rclcpp::Duration &period)
    {
        // TODO: all of it
        (void)time;
        (void)period;
        return controller_interface::return_type::OK;
    }

    controller_interface::CallbackReturn TibbleController::on_deactivate(const rclcpp_lifecycle::State &)
    {
        RCLCPP_INFO(get_node()->get_logger(), "Deactivated TibbleController.");
        return CallbackReturn::SUCCESS;
    }

} // namespace tibble_controller

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(tibble_controller::TibbleController,
                       controller_interface::ControllerInterface)
