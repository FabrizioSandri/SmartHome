let dailyConsumedEnergyChart;
let monthlyConsumedEnergyChart;
let dailyTemperaturesChart;

function getAverages(generalInformation, date) {

    let avgs = {
        "externalTemperature" : [],
        "modulation" : []
    }
    
    let dataForDate = Object.keys(generalInformation).length > 0;
    if (!dataForDate){
        return avgs;
    }

    for (let hour=0; hour<24; hour++){
        paddedHour = (hour <= 9 ? `0${hour}` : `${hour}`);
        let timestamp = Date.parse(`${date} ${paddedHour}:00`)/1000;
        let rangeStart = timestamp - 1800;
        let rangeEnd = timestamp + 1800;
        
        let externalTemperature = 0;
        let modulation = 0;
        let n = 0;
        for (var i = 0; i < generalInformation["dateTime"].length; i++) {
            if (generalInformation["dateTime"][i] >= rangeStart && generalInformation["dateTime"][i] < rangeEnd){
                externalTemperature += generalInformation["externalTemperature"][i];
                modulation += generalInformation["modulation"][i];
                n++;
            } 
        }
        
        if (n!=0){
            externalTemperature /= n;
            modulation /= n;
            avgs["externalTemperature"].push(externalTemperature);
            avgs["modulation"].push(modulation);
        }else{
            avgs["externalTemperature"].push(null);
            avgs["modulation"].push(null);
        }
        
        
    }

    return avgs;
}

function getConsumedEnergyDaily() {
    date = document.getElementById("day").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            
            consumedEnergy = JSON.parse(this.responseText)

            // total daily consumed energy
            totalDailyConsumed = 0;
            for (let i = 0; i < consumedEnergy.measure.length; i++) {
                totalDailyConsumed += consumedEnergy.measure[i];
            }
            document.getElementById("totalDailyConsumed").innerText = `Consumo totale: ${totalDailyConsumed} kWh`

            // if the chart already exists destroy it and regenerate a new one
            if (dailyConsumedEnergyChart) { 
                dailyConsumedEnergyChart.destroy();
            }

            var xhttp2 = new XMLHttpRequest();
            xhttp2.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200){

                    generalInformation = JSON.parse(this.responseText)
                    avgGeneralInformation = getAverages(generalInformation, date)
            
                    dailyConsumedEnergyChart = new Chart("energyConsumed-chart", {
                        data: {
                            labels: consumedEnergy.hours,
                            datasets: [
                                { 
                                    type: "custom_line",
                                    data: avgGeneralInformation["externalTemperature"],
                                    label: "Temperatura esterna",
                                    position: "start",
                                    backgroundColor: "rgb(255, 99, 132)",
                                    borderColor: "rgb(255, 99, 132)",
                                    borderWidth: 2.2,
                                    pointRadius: 3,
                                    pointHoverRadius: 3,
                                    yAxisID: "yExternalTemperature",
                                    units: "°C"
                                },{ 
                                    type: "custom_line",
                                    data: avgGeneralInformation["modulation"],
                                    label: "Modulazione",
                                    borderColor: "#1e3aa7",
                                    backgroundColor: "#1e3aa7",
                                    borderWidth: 2.2,
                                    pointRadius: 3,
                                    pointHoverRadius: 3,
                                    yAxisID: "yModulation",
                                    units: "%"
                                },{ 
                                    type: 'bar',
                                    data: consumedEnergy.measure,
                                    label: "Consumo energetico",
                                    borderColor: "rgba(44, 62, 80, 0.6)",
                                    backgroundColor: "rgba(44, 62, 80, 0.2)",
                                    borderWidth: 2.2,
                                    yAxisID: "yConsumedEnergy",
                                    units: "kW/h"
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
                                    }
                                },
                                yConsumedEnergy: {
                                    display: true,
                                    position: "left",
                                    title: {
                                        display: true,
                                        text: 'Consumo - kW/h'
                                    },
                                    beginAtZero: true,
                                    max: Math.max.apply(null, consumedEnergy.measure) + 0.5
                                },
                                yExternalTemperature: {
                                    display: true,
                                    position: "right",
                                    grid: {
                                        display: false,
                                    },
                                    title: {
                                        display: true,
                                        text: 'Temperatura esterna - °C'
                                    },
                                    max: Math.round(Math.max.apply(null, avgGeneralInformation["externalTemperature"]) + 1.0)
                                },
                                yModulation: {
                                    display: false,
                                    position: "right",
                                    grid: {
                                        display: false,
                                    },
                                    title: {
                                        display: true,
                                        text: 'Modulazione - %'
                                    },
                                    max: 110
                                }
                            },
                            plugins: {
                                tooltip: {
                                    intersect: false,
                                    callbacks: {
                                        title: function(TooltipItems){
                                            return "Orario: " + TooltipItems[0].label ;
                                        },
                                        label: (TooltipItem) => {
                                            return `${TooltipItem.dataset.label}: ${TooltipItem.formattedValue} ${TooltipItem.dataset.units}`;
                                        }
                                    }
                                }
                            }
                            
                        }
                    });
                    
                }
            }
            
            xhttp2.open("GET", "buderus/getGeneralInformation?date=" + date, true);
            xhttp2.send();
            
        }
    }
    
    xhttp.open("GET", "buderus/energyConsumedDaily?date=" + date, true);
    xhttp.send();
}

function trimTemperaturesNonZero(temperatures){

    var i = temperatures.boilerTemperatures.length - 1;
    while (i >= 0 && temperatures.boilerTemperatures[i] == 0) {
        i--;
    }

    temperatures.boilerTemperatures = temperatures.boilerTemperatures.slice(0,i+1);
    temperatures.hours = temperatures.hours.slice(0,i+1);
    for (var t=0; t<temperatures.heatingCircuits.length; t++){
        temperatures.heatingCircuits[t] = temperatures.heatingCircuits[t].slice(0,i+1);
    }

    return temperatures;
}

function getTemperatures() {
    date = document.getElementById("day").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){

            temperatures = trimTemperaturesNonZero(JSON.parse(this.responseText));

            // if the chart already exists destroy it and regenerate a new one
            if (dailyTemperaturesChart) { 
                dailyTemperaturesChart.destroy();
            }

            dailyTemperaturesChart = new Chart("temp-chart", {
                type: 'custom_line',
                data: {
                    labels: temperatures.hours,
                    datasets: [
                        { 
                            data: temperatures["heatingCircuits"][0],
                            label: "HC1",
                            borderColor: "#0e9aa7",
                            backgroundColor: "#0e9aa7",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3,
                            hidden: true
                        },
                        { 
                            data: temperatures["heatingCircuits"][1],
                            label: "Piano 1",
                            borderColor: "#f3622d",
                            backgroundColor: "#f3622d",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3
                        },
                        { 
                            data: temperatures["heatingCircuits"][2],
                            label: "Piano 2",
                            borderColor: "#fbab25",
                            backgroundColor: "#fbab25",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3
                        },
                        { 
                            data: temperatures["heatingCircuits"][3],
                            label: "Piano 3",
                            borderColor: "#57b757",
                            backgroundColor: "#57b757",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3
                        },
                        { 
                            data: temperatures["boilerTemperatures"],
                            label: "Acqua sanitaria ",
                            borderColor: "#1e3aa7",
                            backgroundColor: "#1e3aa7",
                            fill: false,
                            borderWidth: 2.5,
                            pointRadius: 3,
                            pointHoverRadius: 3
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
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Temperatura - °C'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            intersect: false,
                            callbacks: {
                                title: function(TooltipItems){
                                    return `Ore ${TooltipItems[0].label} `;
                                },
                                label: (TooltipItem) => {
                                    return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' °C';
                                }
                            }
                        }
                    }
                }
            });
            
        }
    }
    
    xhttp.open("GET", "/buderus/temperatures?date=" + date, true);
    xhttp.send();
}

function displayDailyCharts() {
    getConsumedEnergyDaily();
    getTemperatures();
}

// crea dinamicamente il bottone di input mensile
function generateOptionsMonthly(idMese, idAnno){
    var optionMese = document.getElementById(idMese);
    var optionAnno = document.getElementById(idAnno);

    var currentYear = new Date().getFullYear();
    var startYear = 2021; // dati dal 2021 in poi

    var years = [];
    var months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

    while (startYear <= currentYear){
        years.push(currentYear--);
    }

    years.forEach((year) => {
        let optionYear = document.createElement("option");
        optionYear.setAttribute("value", "" + year);
        optionYear.innerText = year;

        optionAnno.appendChild(optionYear);
    });

    months.forEach((month) => {
        let optionMonth = document.createElement("option");
        optionMonth.setAttribute("value", "" + month);
        optionMonth.innerText = month;

        optionMese.appendChild(optionMonth);
    });
}

function getConsumedEnergyMonthly() {
    year = document.getElementById("anno").value;
    month = document.getElementById("mese").value;
    
    if (month < 10) { // fix mesi senza 0 davanti
        month = "0" + month;
    }

    var date = year + "-" + month;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){

            consumedEnergy = JSON.parse(this.responseText)
            
            // total monthly consumed energy
            totalMonthlyConsumed = 0;
            for (let i = 0; i < consumedEnergy.measure.length; i++) {
                totalMonthlyConsumed += consumedEnergy.measure[i];
            }
            document.getElementById("totalMonthlyConsumed").innerText = `Consumo totale: ${totalMonthlyConsumed} kWh`
            
            // average consumed energy
            monthlyAverage = 0;
            consumedEnergy.measure.forEach(function (num) { monthlyAverage += num });
            monthlyAverage = monthlyAverage / consumedEnergy.measure.length;
            

            // if the chart already exists destroy it and regenerate a new one
            if (monthlyConsumedEnergyChart) { 
                monthlyConsumedEnergyChart.destroy();
            }
            
            monthlyConsumedEnergyChart = new Chart("energyConsumedMonthly-chart", {
                type: 'bar',
                data: {
                    labels: consumedEnergy.days,
                    datasets: [
                        { 
                            data: consumedEnergy.measure,
                            label: "Consumo energetico",
                            borderColor: "rgba(44, 62, 80, 0.6)",
                            backgroundColor: "rgba(44, 62, 80, 0.2)",
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
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
                            title: {
                                display: true,
                                text: 'Giorno'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Consumo energetico- kW/h'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            intersect: false,
                            callbacks: {
                                title: function(TooltipItems){
                                    return "Giorno: " + TooltipItems[0].label;
                                },
                                label: (TooltipItem) => {
                                    return "Consumo: " + TooltipItem.formattedValue + ' kW';
                                }
                            }
                        },
                        annotation: {
                            annotations: {
                                mean: {
                                    type: 'line',
                                    yMin: monthlyAverage,
                                    yMax: monthlyAverage,
                                    borderColor: 'rgb(255, 99, 132)',
                                    borderWidth: 2,
                                    label: {
                                        enabled: true,
                                        content: "Media",
                                        backgroundColor: "transparent",
                                        color: 'rgb(255, 99, 132)',
                                        position: "start",
                                        backgroundColor: "rgba(255,255,255,1)"
                                    }
                                }
                            }
                        }
                    }
                }
            });
            
        }
    }
    
    xhttp.open("GET", "buderus/energyConsumedMonthly?date=" + date, true);
    xhttp.send();
}

function getHeaderData() {

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){

            data = JSON.parse(this.responseText)
            
            document.getElementById("temperaturaEsterna").innerText = data["temperaturaEsterna"] + " °C";
            document.getElementById("modulazionePompa").innerText = data["modulazionePompa"] + " %";
            document.getElementById("temperaturaMandata").innerText = data["temperaturaMandata"] + " °C";
            document.getElementById("setpointAttuale").innerText = data["setpointAttuale"] + " °C";
            document.getElementById("temperaturaAttuale").innerText = data["temperaturaAttuale"] + " °C";
            
            // creazione tabella circuiti di riscaldamento
            setPointAmbienteRow = document.getElementById("setPointAmbiente");
            temperaturaAmbienteRow = document.getElementById("temperaturaAmbiente");
            temperaturaMandataHcRow = document.getElementById("temperaturaMandataHc");
            
            // hc parte da 2 in quanto non siamo interessati a hc 1 (piano 0)
            for (let hc = 1; hc < data["temperatureHc"]["setPointAmbiente"].length; hc++) {

                let valSetPointAmbiente = document.createElement("td")
                let valtemperaturaAmbiente = document.createElement("td")
                let valtemperaturaMandata = document.createElement("td")

                valSetPointAmbiente.innerText = data["temperatureHc"]["setPointAmbiente"][hc] + " °C";
                valtemperaturaAmbiente.innerText = data["temperatureHc"]["temperaturaAmbiente"][hc] + " °C";
                valtemperaturaMandata.innerText = data["temperatureHc"]["temperaturaMandata"][hc] + " °C";

                setPointAmbienteRow.appendChild(valSetPointAmbiente);
                temperaturaAmbienteRow.appendChild(valtemperaturaAmbiente);
                temperaturaMandataHcRow.appendChild(valtemperaturaMandata);
            }
        }
    }
    
    xhttp.open("GET", "buderus/getGeneralData", true);
    xhttp.send();
}