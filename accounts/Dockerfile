FROM python:3.10
COPY . /accounts
WORKDIR /accounts
RUN ["pip3", "install", "-r", "requirements.txt"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:1984"]