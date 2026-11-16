#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string>

#include "clock.hpp"
#include "event_client.hpp"

int main() {
    std::cout << "Hello, world!\n";

    ClockConfig config{};
    const char* tick_interval_ms = std::getenv("TICK_INTERVAL_MS");

    if (tick_interval_ms != nullptr) {
        config.period = std::chrono::milliseconds(std::stoll(tick_interval_ms));
    }

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
