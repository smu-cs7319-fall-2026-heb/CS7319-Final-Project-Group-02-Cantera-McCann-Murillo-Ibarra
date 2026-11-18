#ifndef EVENT_CLIENT_HPP
#define EVENT_CLIENT_HPP

#include <cstdint> 
#include <string> 

#include <boost/asio/io_context.hpp> 
#include <boost/asio/ip/tcp.hpp> 
#include <boost/mqtt5.hpp>

class EventClient {
private: 
    boost::mqtt5::mqtt_client<boost::asio::ip::tcp::socket> _client; 

public: 
    EventClient(boost::asio::io_context& ioc, const std::string& host, 
                std::uint16_t port); 

    void publish(const std::string& topic, const std::string& payload); 
}; 


#endif // EVENT_CLIENT_HPP 
