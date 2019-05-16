# Openwebnet-webthings

A [webthings](https://iot.mozilla.org/docs/) service for [openwebnet](https://www.myopen-legrandgroup.com/)

# Dependencies

This depends on the reopenwebnet python library. It can be installed like this:

    pip3 install reopenwebnet

# Usage

First edit the configuration file to describe your openwebnet-controlled devices.
There is an example in this directory: `openwebnet-webthings.example.yaml`

Next, start the webthings service:

    python openwebnet-webthings.py <your-config-file>

Finally, import the webthings via the service url (e.g. http://localhost:8888). Make sure to replace 'localhost' with the correct hostname if your Mozilla iot gateway and your webthings service are not running on the same node.
