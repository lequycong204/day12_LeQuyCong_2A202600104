FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build
COPY app/requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV OPENAI_API_KEY=""

WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder /install /usr/local
COPY app /app

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
