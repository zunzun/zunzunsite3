
function submitenter(myfield,e)
{
var keycode;
if (window.event)
    keycode = window.event.keyCode;
else if (e)
    keycode = e.which;
else
    return true;

if (keycode == 13)
   {
       xmlhttpPost("/EvaluateAtAPoint/");
       return false;
   }
else
   return true;
}

function xmlhttpPost(strURL) {
    var xmlHttpReq = false;
    var self = this; // oddly, firefox needs this for this function to work properly
    if (window.XMLHttpRequest) { // non-IE
        self.xmlHttpReq = new XMLHttpRequest();
    }
    else if (window.ActiveXObject) { // IE
        self.xmlHttpReq = new ActiveXObject("Microsoft.XMLHTTP");
    }
    else {
        self.updatepage('I was unable to create AJAX XMLHttpRequest object on your browser.');
        return;
    }
    self.xmlHttpReq.open('POST', strURL, true);
    self.xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    self.xmlHttpReq.onreadystatechange = function() {
        if (self.xmlHttpReq.readyState == 4) {
            updatepage(self.xmlHttpReq.responseText);
        }
    }
    self.xmlHttpReq.send(getquerystring());
}

function getquerystring() {
    var form = document.forms['evaluatePointForm'];
    qstr = 'x=' + escape(form.x.value);
    {% ifequal dimensionality '3' %}
        qstr = qstr + '&amp;y=' + escape(form.y.value);
    {% endifequal %}
    return qstr;
}

function updatepage(str){
    document.getElementById("evaluateResultDiv").innerHTML = str;
}

