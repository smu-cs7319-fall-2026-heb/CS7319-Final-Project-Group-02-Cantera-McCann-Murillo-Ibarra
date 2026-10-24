#include "clock.hpp"

#include <string>

#include <boost/system/error_code.hpp>

const std::string PREFIX = "c2/connector-state/clock";

Clock::Clock(const ClockConfig& config)
    :
    _config(config),
    _bottom_domain(_ioc, _config.host, _config.port),
    _steady_timer(_ioc),
    _tick(0)
{
}

void Clock::run() {
    _steady_timer.expires_at(std::chrono::steady_clock::now() + _config.period);
    schedule_next_tick();
    _ioc.run();
}

void Clock::schedule_next_tick() {
    _steady_timer.async_wait([this](const boost::system::error_code& ec) {
        if (ec) {
            return;
        }
        notify_next_tick();
        _steady_timer.expires_at(_steady_timer.expiry() + _config.period);
        schedule_next_tick();
    });
}

void Clock::notify_next_tick() {
    ++_tick;
    _bottom_domain.publish(PREFIX + "/next_tick", std::to_string(_tick));
}
