FROM python:3.10

ENV PORT=4000

WORKDIR /international-delivery-service-backend

COPY poetry.lock pyproject.toml /international-delivery-service-backend/

RUN pip install --upgrade --no-cache-dir pip==23.1.2 && \
    pip install -U --no-cache-dir poetry==1.7.1 && \
    poetry config --local virtualenvs.create false && \
    poetry install

COPY . .
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.app:app --reload --use-colors --host 0.0.0.0 --port $PORT"]
