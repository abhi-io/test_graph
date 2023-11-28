FROM python:3.10

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1 
WORKDIR /video_library
COPY . .
RUN apt-get update
#RUN apt-get install -y git python3.8 python3.8-dev
#RUN apt update && apt-get install -y python3-pip
#RUN apt-get install -y tesseract-ocr tesseract-ocr-mal libopencv-dev python3 python3-pip python3-opencv
#RUN apt-get update && apt-get install -y libsndfile1 ffmpeg
RUN pip install -r  requirements.txt
#CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "main_module.wsgi:application"]
