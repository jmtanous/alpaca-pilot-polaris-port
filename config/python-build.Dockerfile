FROM benro-dev-tools:bookworm
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran-arm-linux-gnueabi autoconf automake libtool \
    pkg-config patchelf git perl bison flex gettext texinfo \
    libssl-dev zlib1g-dev libbz2-dev liblzma-dev libffi-dev libsqlite3-dev \
    libreadline-dev libncurses-dev uuid-dev python3-dev python3-venv \
    gcc-12-source libgmp-dev libmpfr-dev libmpc-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /project
