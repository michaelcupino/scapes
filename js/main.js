var jsString = "Hello from JavaScript!";
var printMessage = function(msg) {
  document.getElementById('msg').innerHTML = "Message: " + msg;
};

revisionCount = 0;
function setRevisionCount(count) {
  revisionCount = count;
}
