function getCallsLog() {

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200){
          if (this.responseText.toString() == "-1"){
              $('#errormodal').modal('show');
              document.getElementById("error_res").innerText = "Si è verificato un errore.";
              return;
          }
          let data = JSON.parse(this.responseText)
          
          data.forEach(call => {
            let row = document.createElement("tr");
            let calltype = "in ingresso";
            let number;
            if (call[6] == "1"){  // outgoing calls
              number = call[2];
              calltype = "In uscita";
            }else{
              number = call[1];
            }

            row.innerHTML = `<td>${call[0]}</td><td>${number}</td><td>${call[4]}</td><td>${calltype}</td>`

            document.getElementById("callsLog").appendChild(row);
          });
          
      }
  }
  
  xhttp.open("GET", "telephone/callsLog", true);
  xhttp.send();
}