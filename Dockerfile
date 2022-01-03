FROM python:3.10-alpine

WORKDIR /opt

COPY requiremnts.txt .
RUN pip install -r requiremnts.txt

COPY . .

ENTRYPOINT ["python", "bot.py"]
