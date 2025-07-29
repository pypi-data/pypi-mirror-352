ARG IMAGE_BASE=python:3-slim
FROM $IMAGE_BASE

# Install dependencies
RUN apt update \
 && apt install -y --no-install-recommends \
      entr \
      git \
      wget \
 && wget -O ./git-cliff.deb -q https://github.com/orhun/git-cliff/releases/download/v2.5.0/git-cliff-2.5.0.deb \
 && apt install -y --no-install-recommends ./git-cliff.deb \
 && rm -f ./git-cliff.deb \
 && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY --from='requirements' ./pages.txt /tmp/
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 \
 && pip3 install -q -r /tmp/pages.txt --no-cache-dir --upgrade \
 && rm -f /tmp/pages.txt

# Install playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
RUN playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
