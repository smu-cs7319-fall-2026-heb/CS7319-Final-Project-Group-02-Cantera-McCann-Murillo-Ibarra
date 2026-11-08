#include <iostream>

#include "clock.hpp"
#include "event_client.hpp"

int main() {
    std::cout << "Hello, world!\n";

    ClockConfig config{};
    boost::asio::io_context ioc;
    EventClient events(ioc, config.host, config.port);

    Clock clock(
        config, ioc,
        [&events](const std::string& topic, const std::string& payload) {
            events.publish(topic, payload);
        });
    clock.run();

    return 0;
}
