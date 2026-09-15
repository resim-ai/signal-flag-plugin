FROM public.ecr.aws/docker/library/python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS test
RUN python -m pip install --no-cache-dir --only-binary=:all: uv==0.9.26
WORKDIR /plugin
COPY reader/ ./reader/
COPY scripts/setup_reader.py ./scripts/setup_reader.py
RUN mkdir /test-results \
    && python -c "import platform, sys; assert platform.system() == 'Linux'; assert sys.version_info[:2] == (3, 12); print(sys.version); print(platform.machine())" > /test-results/runtime.txt \
    && uv --version >> /test-results/runtime.txt \
    && python scripts/setup_reader.py --state-dir /tmp/signal-flag-reader-test > /test-results/setup.json \
    && python scripts/setup_reader.py --state-dir /tmp/signal-flag-reader-test --check > /test-results/check.json

FROM scratch AS test-results
COPY --from=test /test-results/ /
