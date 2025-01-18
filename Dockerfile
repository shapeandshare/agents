FROM python:3.12

WORKDIR /usr/src/app

COPY requirements/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY dist/shapeandshare.agents-0.1.0-py3-none-any.whl ./
RUN pip install ./shapeandshare.agents-0.1.0-py3-none-any.whl
