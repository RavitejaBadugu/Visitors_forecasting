FROM python:3.8.8-slim
COPY . ~/Fastapi
WORKDIR ~/Fastapi
RUN pip install -r requriements.txt
CMD uvicorn main_map:app --host 0.0.0.0 --port 8000 --reload