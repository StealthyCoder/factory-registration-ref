FROM debian:testing-slim@sha256:bd11994e9931b5228121e5407c47f80d02e4ae8e6fd9a57fed3a3c81fb17e083
LABEL maintainer="stealthycoder@stealthycoder.com"

ENV POETRY_CACHE_DIR=/data/pypoetry

RUN apt update && \    
    apt install -y --no-install-recommends ca-certificates \
    sudo \
    vim \
    bash \
    wget \
    unzip \
    python3 \
    python3-poetry \
    python3-cachecontrol \
    python3-pip && \
    useradd -u 1000 -m -s /bin/bash stealthy-adm && \
    useradd -u 1001 -m -s /bin/bash stealthy && \
    useradd -u 1002 -m -s /bin/bash stealthy-alt && \
    useradd -u 501 -m -s /bin/bash stealthy-mac && \
    useradd -u 502 -m -s /bin/bash stealthy-mac-alt && \
    echo "%adm ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "Set disable_coredump false" >> /etc/sudo.conf && \
    addgroup stealthy-adm adm && \
    addgroup stealthy adm && \
    addgroup stealthy-alt adm && \
    addgroup stealthy-mac adm && \
    addgroup stealthy-mac-alt adm && \
    mkdir -p /srv/http /data/pypoetry /var/lib/augmented/ && \
    python3 -m pip install --upgrade pip setuptools && \
    chown stealthy:stealthy -R /srv && \
    echo -e '#!/bin/bash\n\
    sudo chown -R $(id -u):$(id -g) /srv /var/lib/augmented/\n\
    sudo chown -R $(id -u):$(id -g) /data/pypoetry\n\
    poetry install \n\
    pushd &>/dev/null .boot\n\
    shopt -s globstar \n\
    compgen -G **/*.sh > /dev/null && \
    for script in $(ls **/*.sh)\n\
    do\n\
    tr -d ''"\\015"'' < "$script" > "/var/lib/augmented/$script"\n\
    chmod +x "/var/lib/augmented/$script"\n\
    "/var/lib/augmented/$script"\n\
    done\n\
    popd &>/dev/null\n\
    /bin/bash -l -c "$*" \n\
    ' >> /srv/entrypoint.sh  && \
    chmod +x /srv/entrypoint.sh && \
    sed -i 's/-e //' /srv/entrypoint.sh

ENTRYPOINT [ "/srv/entrypoint.sh" ]
WORKDIR /srv/http
USER stealthy:stealthy

COPY ./data/certs ../certs

CMD ["/usr/bin/poetry", "run", "uvicorn", "app:app", "--reload", "--host", "0.0.0.0"]
