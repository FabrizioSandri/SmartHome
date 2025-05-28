function getCurrentUsageGraph(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById("panel").innerHTML = this.responseText;
        }
    }
    
    xhttp.open("GET", "batteriesUsageChart", true);
    xhttp.send();
    
}

function getBatteryPercentage(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById("batterypercentageprogress").setAttribute("aria-valuenow", this.responseText);
            document.getElementById("batterypercentage").innerHTML = this.responseText + "%";
        }
    }
    
    xhttp.open("GET", "batteryPercentage", true);
    xhttp.send();
    
}

function sendBoost(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4){
            res = JSON.parse(this.responseText);
            if (this.status == 200){
                document.getElementById("boostresult").innerHTML = res["msg"];
            }else{
                document.getElementById("boostresult").innerHTML = res["error"];
            }
        }else if(this.readyState == 4 && this.status != 200){
        }
    }
    
    xhttp.open("POST", "boost", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("endtime=" + document.getElementById("endtime").value);
}

function getE4uOnlineData(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            jsonResponse = JSON.parse(this.responseText);

            if ("error" in jsonResponse){
                document.getElementById("reducerstatus").innerText = jsonResponse["error"];
            }else{
                document.getElementById("reducerstatus").innerText = jsonResponse["status"];

                if (jsonResponse["status"] == "BOOST"){
                    document.getElementById("reducerremainingtime").innerText = "-> tempo boost rimanente " + jsonResponse["boostRemaining"];
                    
                }else {
                    document.getElementById("reducerremainingtime").innerText = "";
                }
            }

        }
    }
    
    xhttp.open("GET", "e4u_data", true);
    xhttp.send();
    
}


function changePowerReducerStatus(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById("switchresult").innerHTML = this.responseText;
        }
    }
    
    let status = "off";
    radios = document.getElementsByName("switchresistenza"); // get the radio buttons value
    for (var i=0; i<radios.length; i++) {
        if (radios[i].checked) {
            status = radios[i].value
            break;
        }
    }

    xhttp.open("POST", "changePowerReducerStatus", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("status=" + status );
}

// get weekly power reducer timers
function generateScheduleTimer() {

    document.getElementById("schedule_legend").hidden = false;
    document.getElementById("schedule").innerText = "Attendi, ci vorra' un attimo...";

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            generateScheduleChart(JSON.parse(this.responseText));
        }
    }
    
    xhttp.open("GET", "getPowerReducerSchedule", true);
    xhttp.send();
}

// generate dinamically the weekly schedule table
function generateScheduleChart(weeklySchedule){                

    // reset div
    document.getElementById("schedule").innerText = "";

    const scheduleContainer = document.getElementById("schedule");
    const days = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"];

    // div contenente la riga degli orari
    const hoursDiv = document.createElement("div");
    hoursDiv.classList.add("row");
    
    // label iniziale (vuoto - spacing)
    const emptyLabel = document.createElement("p");
    emptyLabel.classList.add("daylabel");
    hoursDiv.appendChild(emptyLabel);

    for(var timeSlot=0; timeSlot<12; timeSlot++){
        let divSlot = document.createElement("div");
        divSlot.classList.add("hourslot");
        divSlot.innerText = timeSlot*2 + ":00";
        
        hoursDiv.appendChild(divSlot);
    }

    scheduleContainer.appendChild(hoursDiv);


    // tabella sottostante
    for(var i=0; i<7; i++){
        let schedule = weeklySchedule[i];
        schedule = schedule.split(";");

        // div contenente la riga del singolo giorno
        const dayDiv = document.createElement("div");
        dayDiv.id = "day" + i;
        dayDiv.classList.add("row");
        
        // label giorno
        const dayLabel = document.createElement("p");
        dayLabel.classList.add("daylabel");
        dayLabel.innerText = days[i];
        dayDiv.appendChild(dayLabel);

        for(var timeSlot=0; timeSlot<48; timeSlot++){
            let divSlot = document.createElement("div");
            divSlot.classList.add("slot"+schedule[timeSlot]);
            divSlot.classList.add("timeslot");
            
            dayDiv.appendChild(divSlot);
        }

        scheduleContainer.appendChild(dayDiv);
    }
}

// updates the daily production field based on the date input
function getDailyProduction(date, elementId){

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            document.getElementById(elementId).innerHTML = this.responseText + " kWh";
        }else if(this.readyState == 4){
            document.getElementById(elementId).innerHTML = "0 kWh"
        }
    }
    
    xhttp.open("GET", "getEnergyProduced?date=" + date, true);
    xhttp.send();
}

let actualChart = undefined;
function displayCharts(powerProduced, powerProducedCompare) {

    if (actualChart){
        actualChart.destroy();
    }


    actualChart = new Chart("production-chart", {
        type: 'custom_line',
        data: {
            labels: powerProduced["time"],
            datasets: [
                { 
                    data: powerProduced["value"],
                    label: "Energia prodotta",
                    backgroundColor: "rgba(251, 192, 45, 0.4)",
                    borderColor: "#e67e22",
                    fill: true,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 1,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4
                },
                { 
                    data: powerProducedCompare["value"],
                    label: "Confronto energia prodotta",
                    backgroundColor: "rgba(81, 81, 81, 0.2)",
                    borderColor: "rgba(81, 81, 81, 0.8)",
                    fill: true,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 1,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4
                }
            ]
        },
        options: {
            interaction: {
                mode: 'nearest',
                axis: 'x'
            },
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Orario'
                    },
                    ticks: {
                        maxTicksLimit: 12
                    },
                    grid: {
                        color: "#7F7F7F"
                    },
                    border: {
                        dash: [8, 4]
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Energia prodotta (kW/h)'
                    },
                    grid: {
                        color: "#7F7F7F"
                    },
                    border: {
                        dash: [8, 4]
                    },
                    ticks: {
                        count: 7
                    }
                }
            },
            plugins: {
                tooltip: {
                    intersect: false,
                    callbacks: {                        
                        title: function(TooltipItems){
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' kW/h';
                        }
                    }
                }
            }
        }
    });

}


function generateProductionChartData(withCompare){

    let todayDate = document.getElementById("day_production").value;
    let compareDate = document.getElementById("day_production_compare").value;

    getDailyProduction(todayDate, "dailyenergygenerated");
   
    if (withCompare){
        getDailyProduction(compareDate, "dailyenergygenerated_compare");
    }

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            
            let todayData = this.responseText;

            if (withCompare){
                let xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200){
                        displayCharts(JSON.parse(todayData), JSON.parse(this.responseText));
                    }
                }
                
                xhttp.open("GET", `getDailySolarPower?date=${compareDate}`, true);
                xhttp.send();
            }else{
                displayCharts(JSON.parse(todayData), []);
            }
            
        }
    }
    
    xhttp.open("GET", `getDailySolarPower?date=${todayDate}`, true);
    xhttp.send();
    
}


// updates the date element specified by elementId by moving the date forward or backward by a day 
function updateDateDirection(direction, elementId){
    let fulldate = document.getElementById(elementId).value;

    let date = new Date(fulldate);
    date.setDate( date.getDate() + direction );
    fulldate = date.toISOString().split('T')[0];
    document.getElementById(elementId).value = fulldate;

    if (elementId == "day_production"){
        generateProductionChartData(false);
    }else{
        generateProductionChartData(true);
    }
}