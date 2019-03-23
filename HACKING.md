# Building Images
Container sources are formatted into descriptor files and modules which are digestible by the container image building tool known as [cekit](http://cekit.io/). 

## Cekit build
To install [cekit](http://cekit.io/) run:
`dnf install python3-cekit`

To build an image using cekit, run the following in any image directory:
`cekit build`

## Chain build
For building all the images automatically, one can use the `chain.py` script.

Download dependencies for chain tool
`pip3 install -r requirements.txt`

Builds all the images
`./chain.py build`
