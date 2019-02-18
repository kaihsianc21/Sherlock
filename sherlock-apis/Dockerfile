FROM python:3.6-alpine

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true

COPY . /api
WORKDIR /api

# install requirements
RUN pip install -r requirements.txt

RUN pip install gunicorn


# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]