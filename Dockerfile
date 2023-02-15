FROM python:3

RUN pip install -r requirements.txt

CMD uvicorn app.main:app --host localhost --port 8000 --reload
