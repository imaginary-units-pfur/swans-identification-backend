FROM python:3

WORKDIR /app
CMD [ "python3", "./app.py" ]

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
