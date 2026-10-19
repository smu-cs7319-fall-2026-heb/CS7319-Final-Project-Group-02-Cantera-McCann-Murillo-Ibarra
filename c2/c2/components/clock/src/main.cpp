#include <iostream>

#include "clock.hpp"

int main() {
    std::cout << "Hello, world!\n";

    Clock clock(ClockConfig{});
    clock.run();

    return 0;
}
