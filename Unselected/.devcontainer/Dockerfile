FROM ubuntu:26.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    curl \
    g++ \
    make \
    mosquitto-clients \
    python3 \
    python3-matplotlib \
    python3-numpy \
    python3-paho-mqtt \
    python3-pandas \
    python3-scipy

RUN curl -fsSL -o /tmp/boost.tar.gz \
    https://archives.boost.io/release/1.88.0/source/boost_1_88_0.tar.gz \
    && tar xzf /tmp/boost.tar.gz -C /opt boost_1_88_0/boost

CMD ["sleep", "infinity"]
