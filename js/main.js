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
  server.Add(document.getElementById('num1').value,
      document.getElementById('num2').value,
      onAddSuccess);
}

function Request(function_name, opt_argv) {
  if(!opt_argv) {
    opt_argv = new Array();
  }

  var callback = null;
  var len = opt_argv.length;
  if (len > 0 && typeof opt_argv[len-1] == 'function') {
    callback = opt_argv[len-1];
    opt_argv.length--;
  }
  var async = (callback != null);

  var query = 'action=' + encodeURIComponent(function_name);
  for (var i = 0; i < opt_argv.length; i++) {
    var key = 'arg' + i;
    var val = JSON.stringify(opt_argv[i]);
    query += '&' + key + '=' + encodeURIComponent(val);
  }

  var req = new XMLHttpRequest();
  req.open('GET', '/rpc?' + query, async);

  if (async) {
    req.onreadystatechange = function() {
      if (req.readyState == 4 && req.status == 200) {
        var response = null;
        try {
          response = JSON.parse(req.responseText);
        } catch (e) {
          response = req.responseText;
        }
        callback(response);
      }
    }
  }

  req.send(null);
}

function InstallFunction(obj, name) {
  obj[name] = function() {
    Request(name, arguments);
  }
}

var server = {};
InstallFunction(server, 'Add');
