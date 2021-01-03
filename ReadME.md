# Python docker console
A application written in python to provide a websocket based server to connect to console and execute commands in running docker containers from a web based terminal (xtermjs).

```
sudo docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /home/pushpender/Apps/docker-console/console:/src/app/ -p 8766:8766 terminal
```

