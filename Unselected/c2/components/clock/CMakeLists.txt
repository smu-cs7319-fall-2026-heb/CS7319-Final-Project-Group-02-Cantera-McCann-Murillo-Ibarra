cmake_minimum_required(VERSION 3.10)
project(c2)

add_executable(clock src/main.cpp src/event_client.cpp src/clock.cpp)
target_include_directories(clock PRIVATE /opt/boost_1_88_0)
