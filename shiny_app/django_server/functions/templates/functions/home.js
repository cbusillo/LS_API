const updateSocket = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/functions/'
);
$('#status').value = "no message received yet...\n"
updateSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    $('#status').value = data.message +
        '\n' +
        $('#status').value;
};


$('#status').onclick = function (e) {
    console.error("Clicked");
    updateSocket.send(JSON.stringify({
        'message': "sending message from JS"
    }));
};