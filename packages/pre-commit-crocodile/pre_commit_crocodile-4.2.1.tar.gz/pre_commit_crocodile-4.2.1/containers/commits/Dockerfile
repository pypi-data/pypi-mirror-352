ARG IMAGE_BASE=python:3-alpine
FROM $IMAGE_BASE

# Install dependencies
RUN apk add -q --no-cache  \
      gcc \
      git \
      libc-dev

# Install requirements
COPY --from='requirements' ./commits.txt /tmp/
RUN export PIP_DISABLE_PIP_VERSION_CHECK=1 \
 && pip3 install -q -r /tmp/commits.txt --no-cache-dir --upgrade \
 && rm -f /tmp/commits.txt
