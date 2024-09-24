###############################
# --- Python Dependencies --- #
###############################

FROM --platform=linux/amd64 python:3.11 as builder

WORKDIR /build

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir awslambdaric

#################
# --- Final --- #
#################

FROM --platform=linux/amd64 python:3.11-slim

RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG FUNCTION_DIR="/function"
WORKDIR ${FUNCTION_DIR}

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./src/ ${FUNCTION_DIR}/

# Add the RIE
RUN mkdir -p ~/.aws-lambda-rie && \
    wget -O ~/.aws-lambda-rie/aws-lambda-rie \
    https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
    chmod +x ~/.aws-lambda-rie/aws-lambda-rie

# Create the entry script
RUN echo '#!/bin/sh\n\
    if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then\n\
    exec ~/.aws-lambda-rie/aws-lambda-rie python -m awslambdaric $1\n\
    else\n\
    exec python -m awslambdaric $1\n\
    fi' > /entry_script.sh && \
    chmod +x /entry_script.sh

ENTRYPOINT ["/entry_script.sh"]
CMD ["linkedin_post_explorer.aws_lambda_handler.handler"]
