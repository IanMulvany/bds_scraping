# DOCKER-VERSION 1.1.2
FROM python
ADD requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /src
CMD ["python", "/src/scrape_bds.py"]
