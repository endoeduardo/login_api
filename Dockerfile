FROM python:3.12.0

WORKDIR /api

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "api/main.py"]