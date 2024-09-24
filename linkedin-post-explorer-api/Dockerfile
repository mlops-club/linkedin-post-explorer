###############################
# --- Python Dependencies --- #
###############################

FROM --platform=linux/amd64 python:3.11 as builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir awslambdaric

#################
# --- Final --- #
#################

FROM --platform=linux/amd64 python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl && \
    curl -Lo /usr/local/bin/aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
    chmod +x /usr/local/bin/aws-lambda-rie && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ARG FUNCTION_DIR="/function"
WORKDIR ${FUNCTION_DIR}

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./src/ ${FUNCTION_DIR}/

ENTRYPOINT /usr/local/bin/aws-lambda-rie /usr/local/bin/python -m awslambdaric

CMD ["linkedin_post_explorer.aws_lambda_handler.handler"]
