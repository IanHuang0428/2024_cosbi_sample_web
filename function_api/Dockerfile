FROM python:3.10
COPY . /function_api
WORKDIR /function_api
RUN ["pip3", "install", "-r", "requirements.txt"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:1986"]