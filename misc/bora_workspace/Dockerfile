# start by pulling the python image
FROM python:3.8-alpine

EXPOSE 8000

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN python -m pip install -r requirements.txt

# copy every content from the local file to the image
COPY . .

# configure the container to run in an executed manner
ENTRYPOINT [ "python", "app.py" ]

# start by pulling the python image
#FROM python:3.9-alpine

#RUN apk add --update nodejs npm

#EXPOSE 8888 2000

#COPY . /tmp
#WORKDIR /tmp


# install the dependencies and packages in the requirements file
#RUN python -m pip install -r bora/requirements.txt


#CMD ["python", "app.py"]
