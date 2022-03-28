FROM python:3.10-alpine

WORKDIR /opt

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir data

ENTRYPOINT ["python", "bot.py"]
