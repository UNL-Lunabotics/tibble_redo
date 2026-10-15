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
            la_min_ = auto_declare<double>("la_min", 0.0);
            la_max_ = auto_declare<double>("la_max", 0.254);    // TODO: unhardcode this later
            excav_dt_speed_multiplier_ = auto_declare<double>("excav_dt_speed_multiplier", excav_dt_speed_multiplier_);
            digging_threshold_ = auto_declare<double>("digging_threshold", 0.05);
            cmd_timeout_ = auto_declare<double>("cmd_timeout", 0.5);
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
        cmd_buffer_.writeFromNonRT(nullptr);

        cmd_sub_ = get_node()->create_subscription<interfaces::msg::TibbleCommand>(
            cmd_topic_, rclcpp::SystemDefaultsQoS(),
            [this](const interfaces::msg::TibbleCommand::SharedPtr msg)
            {
                // Runs on a non-RT thread (which is why we need the buffer)
                cmd_buffer_.writeFromNonRT(msg);
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

        for (auto &interface : joint_velocity_command_interface_)
        {
            interface.get().set_value(0.0);
        }

        cmd_buffer_.writeFromNonRT(nullptr);

        RCLCPP_INFO(get_node()->get_logger(), "Activated TibbleController.");
        return CallbackReturn::SUCCESS;
    }

    controller_interface::return_type TibbleController::update(const rclcpp::Time &time, const rclcpp::Duration &period)
    {
        const interfaces::msg::TibbleCommand::SharedPtr command = *cmd_buffer_.readFromRT();

        double linear_x = 0.0;
        double angular_z = 0.0;
        double drum_cmd = 0.0;
        double la_cmd = 0.0;
        bool panic = false;

        uint8_t mode = interfaces::msg::TibbleCommand::MODE_DISABLED;

        if (command)
        {
            const double age = (time - rclcpp::Time(command->header.stamp)).seconds();
            if (age <= cmd_timeout_)
            {
                // Command is not stale if it reaches this point, so accept values from it
                mode = command->mode;
                panic = command->panic;
                linear_x = command->linear_x;
                angular_z = command->angular_z;
                drum_cmd = command->drum_cmd;
                la_cmd = command->la_cmd;
            }
            else
            {
                RCLCPP_WARN_THROTTLE(
                    get_node()->get_logger(), *get_node()->get_clock(), 1000,
                    "TibbleCommand is %.2fs old (timeout %.2fs). Commanding zero. Is the supervisor node running?",
                    age, cmd_timeout_);

            }
        }
        else
        {
            RCLCPP_WARN_THROTTLE(
                get_node()->get_logger(), *get_node()->get_clock(), 1000,
                "No TibbleCommand received yet. Commanding zero.");

        }

        // PANIC AND DISABLED
        if (panic || mode == interfaces::msg::TibbleCommand::MODE_DISABLED)
        {
            linear_x = 0.0;
            angular_z = 0.0;
            drum_cmd = 0.0;
            la_cmd = 0.0;
        }

        // Differential drive inverse kinematics
        double left_wheel_vel = (linear_x - angular_z * wheel_separation_ / 2.0) / wheel_radius_;
        double right_wheel_vel = (linear_x + angular_z * wheel_separation_ / 2.0) / wheel_radius_;

        // Slowdown drivetrain while actively digging (this is what the threshold value is for)
        const bool digging = std::abs(drum_cmd) > digging_threshold_;
        if (digging)
        {
            left_wheel_vel *= excav_dt_speed_multiplier_;
            right_wheel_vel *= excav_dt_speed_multiplier_;
        }

        // Drum
        const double drum_vel = std::clamp(drum_cmd, -1.0, 1.0) * paddle_speed_;

        // Linear actuators
        double la_vel = std::clamp(la_cmd, -1.0, 1.0) * la_speed_;
        const double la_position = joint_position_state_interface_[kLaExtend].get().get_value();
        if (!std::isfinite(la_position))
        {
            la_vel = 0.0; // position unknown so refuse to move
        }
        else if (la_vel > 0.0 && la_position >= la_max_)
        {
            la_vel = 0.0;
        }
        else if (la_vel < 0.0 && la_position <= la_min_)
        {
            la_vel = 0.0;
        }

        joint_velocity_command_interface_[kDlRotate].get().set_value(left_wheel_vel);
        joint_velocity_command_interface_[kDrRotate].get().set_value(right_wheel_vel);
        joint_velocity_command_interface_[kLaExtend].get().set_value(la_vel);
        joint_velocity_command_interface_[kExcavationRotate].get().set_value(drum_vel);

        // The supervisor already computes latch and vibe since it's just on/off
        // Additionally, no ros2_control command interface for them (maybe in future?)
        RCLCPP_INFO_THROTTLE(
            get_node()->get_logger(), *get_node()->get_clock(), 500,
            "vel cmds -> DL: %.3f  DR: %.3f  LA: %.3f  drum: %.3f",
            left_wheel_vel, right_wheel_vel, la_vel, drum_vel
        );

        // TODO: odom pub, tf broadcaster, state service

        return controller_interface::return_type::OK;
    }

    controller_interface::CallbackReturn TibbleController::on_deactivate(const rclcpp_lifecycle::State &)
    {
        // Interfaces still active, so just set to safe defaults
        for (auto &interface : joint_velocity_command_interface_)
        {
            interface.get().set_value(0.0);
        }
        cmd_buffer_.writeFromNonRT(nullptr);

        RCLCPP_INFO(get_node()->get_logger(), "Deactivated TibbleController.");
        return CallbackReturn::SUCCESS;
    }

} // namespace tibble_controller

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(tibble_controller::TibbleController,
                       controller_interface::ControllerInterface)
