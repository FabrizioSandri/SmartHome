function load_settings(data) {

    document.getElementById("house_name").value = data["vars"]["house_name"];
    document.getElementById("weather_location").value = data["vars"]["weather_location"];

    document.getElementById("weather_historical_data_location").value = data["weather"]["historical_data_location"];
    document.getElementById("historical_data_prefix").value = data["weather"]["historical_data_prefix"];
    document.getElementById("default_chart_gap").value = data["weather"]["default_chart_gap"];
    
    document.getElementById("download_secret").value = data["buderus"]["download_secret"];
    document.getElementById("buderus_gateway_ip").value = data["buderus"]["gateway_ip"];
    document.getElementById("buderus_historical_data_location").value = data["buderus"]["historical_data_location"];

    document.getElementById("api_key").value = data["solaredge"]["api_key"];
    document.getElementById("site_id").value = data["solaredge"]["site_id"];

    document.getElementById("tesla_gateway_ip").value = data["tesla"]["gateway_ip"];
    document.getElementById("gateway_email").value = data["tesla"]["gateway_email"];

    document.getElementById("device_ip").value = data["elios4you"]["device_ip"];
    document.getElementById("device_port").value = data["elios4you"]["device_port"];


    let cam = 1;
    for(const key in data["surveillance"]){
        document.getElementById(`cam${cam}_name`).innerHTML = key;
        document.getElementById(`cam${cam}_name_hidden`).value = key;
        document.getElementById(`cam${cam}_ip`).value = data["surveillance"][key]["ip"];
        document.getElementById(`cam${cam}_rtsp_port`).value = data["surveillance"][key]["rtsp_port"];
        document.getElementById(`cam${cam}_username`).value = data["surveillance"][key]["username"];
        document.getElementById(`cam${cam}_stream`).value = data["surveillance"][key]["stream"];
        cam++;
    }
}


function save_settings() {

    let maincontainer = document.getElementById("maincontainer");
    let inputs = maincontainer.getElementsByTagName('input');
    let query = "";
    for (let i = 0; i < inputs.length; i++) {
        query += `${inputs[i].id}=${inputs[i].value}&`;
    }
    query = query.slice(0, -1);

    let new_password1 = document.getElementById("new_password1").value;
    let new_password2 = document.getElementById("new_password2").value;
    if (new_password1 != new_password2){
        document.getElementById("save_result").innerHTML = "La password nuova non corrisponde";
        return;
    }

    // send a POST request to the server
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById("save_result").innerHTML = this.responseText;
        }
    }
    
    xhttp.open("POST", "/settings/save", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(query);

}