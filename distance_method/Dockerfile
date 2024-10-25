FROM python:3.10
COPY . /distance_method
WORKDIR /distance_method
RUN ["pip3", "install", "-r", "requirements.txt"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:1985"]