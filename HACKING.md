# Building Images
Container sources are formatted into descriptor files and modules which are digestible by the container image building tool known as [cekit](http://cekit.io/). 

## Cekit build
To install [cekit](http://cekit.io/) run:
`dnf install python3-cekit`

To build an image using cekit, run the following in any image directory:
`cekit build`
