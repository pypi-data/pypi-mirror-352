<p align="center">
  <img alt="Onesait Logo" src="https://raw.githubusercontent.com/onesaitplatform/onesaitplatform-web-template/main/public/img/onesait-brand-logo.svg" width="300"/>
</p>

Onesait Platform Python Client Services
===============================

## What is it?

onesaitplatform-client-services is a Python library that provides several classes that implement the functionalities of different platform clients, enabling applications to connect to a Onesait Platform instance and perform basic CRUD operations.

With this library, you can generate queries, insert data into ontologies, manage REST APIs and their calls, and upload and download binary files, among other things.

Before using the client services for the first time, we strongly recommend that you learn the main concepts of the Onesait Platform platform. 

It supports Python 3.4+

## Main Features

Here are just a few of the things that onesaitplatform-client-services does well:

- Easily create a Digital Client, enabling you to later perform queries, inserts, and updates on the ontologies stored in the Onesait Platform.
    
- Set up an API Manager Client to connect with API Manager and Onesait Platform APIs. You can retrieve API REST information, create a API REST from a JSON object, delete a API REST, make requests to a API REST, and list user APIs, among other features.

- Use a File Manager to perform operations with the binary repository, such as uploading and updating files, downloading files from the binary repository and MinIO, and more.

## How to install it

In order to use this API, you must have `pip` installed in your system. The pip website (https://pypi.python.org/pypi/pip) contains detailed installation instructions.

Once `pip` is installed, you will be able to install the Python clients into your local package repository by running the following commands:

1. To install from download repository:

~~~~~~
pip install .
~~~~~~

~~~~~~
python setup.py install
~~~~~~

2. To install from pypi:

~~~~~~
pip install onesaitplatform-client-services
~~~~~~

## Samples usage

### IotBrokerClient

An example of IotBrokerClient is available in [IotBrokerClient tutorial](https://github.com/onesaitplatform/onesait-cloud-platform-clientlibraries/blob/master/python-client/examples/DigitalClient.ipynb)

### FileManager

An example of FileManager is available in [FileManager tutorial](https://github.com/onesaitplatform/onesait-cloud-platform-clientlibraries/blob/master/python-client/examples/FileManager.ipynb)

### ApiManager

An example of ApiManager is available in [ApiManager tutorial](https://github.com/onesaitplatform/onesait-cloud-platform-clientlibraries/blob/master/python-client/examples/ApiManagerClient.ipynb)

### MQTTClient

An example of FileManager is available in [MqttClient tutorial](https://github.com/onesaitplatform/onesait-cloud-platform-clientlibraries/blob/master/python-client/examples/MqttClient.ipynb) (deprecated)

You can see also how to use the Digital Client, File Manager, and API Manager by visiting this website: https://onesaitplatform.com/space/DOCT/2220787684/How+to+use+Python+API%3F.

## About Onesait Platform

Onesait Platform is an open technology platform developed by Minsait, designed to simplify and accelerate the development of digital solutions. By abstracting the complexity of underlying technical layers, it helps to simplify and standardize developments enabling independence in lower-level technical decisions and providing flexibility in the face of technological changes.

Key features of Onesait Platform include:

- Enabling work with multiple clouds in multi-cloud formats.

- Making cloud and on-premise architectures compatible.

- Managing the complexity of technologies and protocols.

- Optimizing the development of business solutions independent of the technological layer through a LowCode strategy.

- Incorporating best-in-class AI capabilities.

- Maximizing the value of your information with our methodology and algorithms.

You can learn more about what you can do with Onesait Platform by visiting https://onesaitplatform.refined.site/.