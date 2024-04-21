FROM python:3.11

EXPOSE 8080

WORKDIR /app

COPY . ./

ENV GOOGLE_APPLICATION_CREDENTIALS=".key/msds603-eship-306b28ac4748.json"
ENV GOOGLE_CLOUD_PROJECT="msds603-eship"
ENV GCP_PROJECT_NAME="msds603-eship"

RUN pip install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
