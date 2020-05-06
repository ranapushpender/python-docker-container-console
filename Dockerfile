FROM alpine
RUN apk add --no-cache python3
RUN python3 -m pip install asyncio
RUN python3 -m pip install pyjwt
RUN python3 -m pip install requests
RUN python3 -m pip install websockets
RUN mkdir /src
RUN mkdir /src/app
WORKDIR /src/app
EXPOSE 8766/tcp
CMD python3 TerminalSocket.py

