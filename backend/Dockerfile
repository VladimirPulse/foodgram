FROM python:3.9

WORKDIR /app

# RUN pip install -r requirements.txt

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8090", "foodgram.wsgi"]