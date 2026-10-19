#ifndef CLOCK_HPP
#define CLOCK_HPP

#include <chrono>
#include <cstdint>
#include <string>

#include <boost/asio/io_context.hpp>
#include <boost/asio/steady_timer.hpp>

#include "event_client.hpp"

struct ClockConfig {
    std::string host = "connector-state";
    std::uint16_t port = 1883;
    std::chrono::milliseconds period = std::chrono::seconds(1);
};

class Clock {
private:
    ClockConfig _config;
    boost::asio::io_context _ioc;
    EventClient _bottom_domain;
    boost::asio::steady_timer _steady_timer;
    std::uint64_t _tick;

    void schedule_next_tick();
    void notify_next_tick();

public:
    explicit Clock(const ClockConfig& config);
    void run();
};

#endif // CLOCK_HPP
