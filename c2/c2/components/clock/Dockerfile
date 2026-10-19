FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    curl \
    g++ \
    make

RUN curl -fsSL -o /tmp/boost.tar.gz \
    https://archives.boost.io/release/1.88.0/source/boost_1_88_0.tar.gz \
    && tar xzf /tmp/boost.tar.gz -C /opt boost_1_88_0/boost

CMD ["sleep", "infinity"]

