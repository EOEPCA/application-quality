FROM python:3-alpine

RUN pip install flake8 flake8-sarif flake8-json

WORKDIR /apps

ENTRYPOINT ["flake8", "--format=json"]
CMD ["--help"]