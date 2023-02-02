FROM python:3.10-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY help_paw/ .
CMD ["gunicorn", "help_paw.wsgi:application", "--bind", "0:8000" ]