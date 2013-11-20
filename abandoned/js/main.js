var jsString = "Hello from JavaScript!";
var printMessage = function(msg) {
  document.getElementById('msg').innerHTML = "Message: " + msg;
};

revisionCount = 0;
function setRevisionCount(count) {
  revisionCount = count;
}


// AJAX Stuff
function onAddSuccess(response) {
  document.getElementById('result').value = response;
}

function doAdd() {
  $.ajax({
    type: "POST",
    url: "/rpc",
    data: {
      action : "Add",
      arg0 : $("#num1").val(),
      arg1 : $("#num2").val()
    },
    success: onAddSuccess
  });
}

function createLoadResourceToDomFunction(index) {
  return function loadResourceToDom(jqxHR) {
    content = "Loading " + index;
    $(".resources").append(
        "<div class='loading resource-" + index + "'>" + content + "</div>"
    );
  }
}

function loadResourceToDom(jqxHR) {
  content = "Loading 0";
  $(".resources").append(
      "<div class='resource-0'>" + content + "</div>"
  );
}

function createAddResourceToDomFunction(selector) {
  return function addResourceToDom(content) {
    $(selector).html(content);
  }
}

function addResourceToDom(content) {
  $(".resources").append(
      "<div class='resource'>" + content + "</div>"
  );
}
