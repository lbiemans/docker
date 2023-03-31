#! /bin/python3

# $Id: docker_outdated_check.py 50587 2023-03-30 19:42:10Z lbiemans $
# $URL: https://svn.uvt.nl/its-id/trunk/personal/lbiemans/bin/docker_outdated_check.py $

# Python package requirements: docker python-dateutil

import docker
from datetime import datetime

client = docker.from_env()

cnt_outdated = ""
for container in client.containers.list():
  ID=(container.id)
  C_NAME=(container.name)
  C_CREATED=((container.attrs["Created"])[:10])
  C_STARTED=(((container.attrs["State"])['StartedAt'])[:10])
  DATENOW=(datetime.today().strftime('%Y-%m-%d'))
  res = (datetime.strptime(DATENOW, "%Y-%m-%d") - datetime.strptime(C_CREATED, "%Y-%m-%d")).days
  resS = (datetime.strptime(DATENOW, "%Y-%m-%d") - datetime.strptime(C_STARTED, "%Y-%m-%d")).days
  if (res > 28):
    C_OUTDATED = ((cnt_outdated)+(C_NAME))
    cnt_outdated = (C_OUTDATED)

if cnt_outdated != "":
  print(("You have outdated containers: ")+(cnt_outdated))
  nec = ("1")

# Go and look for images that are outdated
imgs_outdated = ""
for image in client.images.list():
  I_NAME=(image)
  I_CREATED=((image.attrs["Created"])[:10])
  DATENOW=(datetime.today().strftime('%Y-%m-%d'))
  resI = (datetime.strptime(DATENOW, "%Y-%m-%d") - datetime.strptime(I_CREATED, "%Y-%m-%d")).days
  if (resI > 28):
    I_OUTDATED = (str((imgs_outdated))+(str(I_NAME)))
    imgs_outdated=(I_OUTDATED)

if imgs_outdated != "":
  print(("You have outdated images:")+imgs_outdated.replace('<Image:','').replace('>',''))
  nec = ("2")

if nec != "0":
  exit(2)
else:
  exit(0)

