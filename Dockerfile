FROM python:3.10-alpine

WORKDIR /opt

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "bot.py"]
