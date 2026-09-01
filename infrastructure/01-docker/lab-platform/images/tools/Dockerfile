FROM alpine:latest

RUN apk add --no-cache \
    bash \
    curl \
    wget \
    jq \
    openssl \
    bind-tools \
    iproute2 \
    iputils \
    netcat-openbsd \
    tcpdump \
    traceroute \
    busybox-extras

WORKDIR /workspace

CMD ["bash"]
