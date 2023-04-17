const updateSocket = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/functions/'
);
$('#status').val("no message received yet...\n");
updateSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    $('#status').val(data.message + '\n' + $('#status').val());
};


$('#status').on('click', function (e) {
    console.error("Clicked");
    updateSocket.send(JSON.stringify({
        'message': "sending message from JS"
    }));
});
