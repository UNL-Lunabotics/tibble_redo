#ifndef SERIAL_COMMS_HPP
#define SERIAL_COMMS_HPP

// includes

namespace serial_comms
{
    class SerialComms
    {
        public:
            // default constructor
            SerialComms() = default;
            // default destructor
            ~SerialComms() {
                disconnect();
            }

            inline void setup() {
                return;
            }

            inline void connect() {
                return;
            }

            inline void disconnect() {
                return;
            }

            inline bool is_connected() const {
                return false;
            }
    };
} // namespace serial_comms

#endif // SERIAL_COMMS_HPP