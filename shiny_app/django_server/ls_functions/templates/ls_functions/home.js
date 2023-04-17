const updateSocket = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/ls_functions/'
);
document.querySelector('#status').value = "no message received yet...\n"
updateSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    document.querySelector('#status').value = data.message +
        '\n' +
        document.querySelector('#status').value;
};


document.querySelector('#status').onclick = function (e) {
    console.error("Clicked");
    updateSocket.send(JSON.stringify({
        'message': "sending message from JS"
    }));
};