FROM python:3.8-slim

WORKDIR /app

COPY . .
RUN pip install -r flask/requirements.txt

COPY scripts/cpu_stress.py /app/scripts/cpu_stress.py

CMD ["sh", "-c", "python app.py"]
