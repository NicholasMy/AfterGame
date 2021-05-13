const socket = io();

socket.on("message", function (data) {
    console.log(data);
    recievedFromSocket(data);
});

socket.on("connect", function (data) {
    console.log("Connected to socket");
});

socket.on("disconnect", function (data) {
    console.log("Disconneted from socket");
});

function sendToSocket(json) {
    socket.send(json);
    console.log("sent " + json);
}

function recievedFromSocket(json) {
    console.log("received " + json);
}