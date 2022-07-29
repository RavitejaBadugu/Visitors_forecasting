FROM python:3.8.8-slim
COPY . ~/streamlit
WORKDIR ~/streamlit
RUN pip install -r requriements.txt
ENTRYPOINT ["streamlit","run"]
CMD [ "app.py" ]