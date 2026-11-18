#include "event_client.hpp"

#include <boost/asio/detached.hpp>

EventClient::EventClient(boost::asio::io_context& ioc,
                         const std::string& host, std::uint16_t port)
    :
    _client(ioc)
{
    _client.brokers(host, port).async_run(boost::asio::detached);
}

void EventClient::publish(const std::string& topic,
                          const std::string& payload) {
    _client.async_publish<boost::mqtt5::qos_e::at_most_once>(
        topic, payload, boost::mqtt5::retain_e::no,
        boost::mqtt5::publish_props{}, boost::asio::detached);
}
