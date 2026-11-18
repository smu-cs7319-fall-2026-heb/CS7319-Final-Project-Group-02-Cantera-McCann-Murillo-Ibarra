#ifndef CLOCK_HPP
#define CLOCK_HPP

#include <chrono>
#include <cstdint>
#include <functional>
#include <string>

#include <boost/asio/io_context.hpp>
#include <boost/asio/steady_timer.hpp>

// a function wrapper to allow injecting the publisher to make mock testing easier 
using Publish = std::function<void(
    const std::string&, const std::string&)>;

struct ClockConfig {
    std::string host = "connector-model";
    std::uint16_t port = 1883;
    std::chrono::milliseconds period = std::chrono::seconds(1);
};

class Clock {
private:
    ClockConfig _config;
    boost::asio::io_context& _ioc;
    // accept a publish function 
    Publish _publish;
    boost::asio::steady_timer _steady_timer;
    std::uint64_t _tick;

    void schedule_next_tick();
    void notify_next_tick();

public:
    Clock(const ClockConfig& config,
          boost::asio::io_context& ioc,
          Publish publish);
    void run();
};

#endif // CLOCK_HPP
