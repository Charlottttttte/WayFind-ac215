FROM ghcr.io/astral-sh/uv:0.9.5 AS uv
FROM python:3.12.12-slim
COPY --from=uv /uv /uvx /bin/
RUN useradd --uid 10001 --create-home app && mkdir /index && chown 10001:10001 /index
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY wayfind_retrieval ./wayfind_retrieval
ENV HOME=/home/app HOST=0.0.0.0 PORT=8000 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    WAYFIND_DATA_PATH=/data/scraped_sheet1.csv WAYFIND_INDEX_DIR=/index
USER 10001:10001
# Bake the embedding model into the image so containers never download it at query time.
RUN /app/.venv/bin/python -c "from wayfind_retrieval.embeddings import MiniLMEmbedder; MiniLMEmbedder().embed(['warm up'])"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
CMD ["/app/.venv/bin/python", "-m", "wayfind_retrieval.api"]
