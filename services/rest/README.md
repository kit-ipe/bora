<!-- ABOUT THE PROJECT -->
## REST service

This is a service that runs a REST server.

### Run script

The port is hardcoded inside the script. This script serves as an example, please update the API structure accordingly.

```
$ python3 pyrest.py
```


### varname.yaml entry

```
rest:
    resolution_x:
        source: http://localhost:5617/api/v1/dma/resolution_x
        type: data
    resolution_y:
        source: http://localhost:5617/api/v1/dma/resolution_y
        type: data
```

### Docker installation

```sh
$ docker image build -t pyrest_docker .
$ docker run --expose 5617 -p 5617:5617 -d pyrest_docker
```

### Known problems

It might happen that you encounter CORS error. This is a rather important feature to take care, if you're system is public facing.
If you system is encapsulated in a secured environment, you might be able to get away with disabling this. The example used here 
does disable the CORS.

This example should serve as a starting point for you to further develop your plugin. This is tested to work with bora.
