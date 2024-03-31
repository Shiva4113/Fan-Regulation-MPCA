
var socket = io.connect('http://' + document.domain + ':' + location.port);

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
            var mediaRecorder = new MediaRecorder(stream);
            var chunks = [];
            // Event handler for when data is available
            mediaRecorder.ondataavailable = function(event) {
                chunks.push(event.data);
            }
            // Event handler for when recording is stopped
            mediaRecorder.onstop = function() {
                var audioBlob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
                socket.emit('audio', audioBlob);
            }
            // Start recording
            mediaRecorder.start();
            // Stop recording after 7 seconds 
            setTimeout(function() {
                mediaRecorder.stop();
            },7000);
        })
        .catch(function(err) {
            console.log('Error accessing microphone:', err);
        });
}
