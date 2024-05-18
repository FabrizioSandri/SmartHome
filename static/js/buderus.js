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
        let paddedHour = (hour <= 9 ? `0${hour}` : `${hour}`);
        let timestamp = Date.parse(`${date} ${paddedHour}:00`)/1000;
        let rangeStart = timestamp ;
        let rangeEnd = timestamp + 3600;
        
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
    let date = document.getElementById("day").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            if (this.responseText.toString() == "-1"){
                $('#errormodal').modal('show');
                document.getElementById("error_res").innerText = "Errore di rete.";
                return;
            }
            let consumedEnergy = JSON.parse(this.responseText)

            // total daily consumed energy
            let totalDailyConsumed = 0;
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

                    if (this.responseText.toString() == "-1"){
                        $('#errormodal').modal('show');
                        document.getElementById("error_res").innerText = "Errore di rete.";
                        return;
                    }

                    let generalInformation = JSON.parse(this.responseText)
                    let avgGeneralInformation = getAverages(generalInformation, date)
            
                    dailyConsumedEnergyChart = new Chart("energyConsumed-chart", {
                        data: {
                            labels: [...Array(24).keys()],
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
                                    units: "°C",
                                    cubicInterpolationMode: 'monotone',
                                    tension: 0.4
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
                                    units: "%",
                                    cubicInterpolationMode: 'monotone',
                                    tension: 0.4
                                },{ 
                                    type: 'bar',
                                    data: consumedEnergy.measure,
                                    label: "Consumo energetico",
                                    borderColor: "rgba(100, 100, 100, 1.0)",
                                    backgroundColor: "rgba(200, 200, 200, 1.0)",
                                    borderWidth: 2.3,
                                    barPercentage: 1.0,
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
                                    },
                                    grid: {
                                        color: "#7F7F7F"
                                    },
                                    border: {
                                        dash: [8, 4]
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
                                    max: Math.max.apply(null, consumedEnergy.measure) + 0.5,
                                    grid: {
                                        color: "#7F7F7F"
                                    },
                                    border: {
                                        dash: [8, 4]
                                    },
                                    ticks: {
                                        count: 6
                                    }
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
                                    max: Math.max.apply(null, avgGeneralInformation["modulation"]) + 10,
                                }
                            },
                            plugins: {
                                tooltip: {
                                    intersect: false,
                                    callbacks: {
                                        title: function(TooltipItems){
                                            return `Fascia oraria: ${TooltipItems[0].label}:00 - ${(parseInt(TooltipItems[0].label) + 1)}:00` ;
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
    
    xhttp.open("GET", "buderus/getDaillyConsumedEnergy?date=" + date, true);
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
    let date = document.getElementById("day").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            
            if (this.responseText.toString() == "-1"){
                $('#errormodal').modal('show');
                document.getElementById("error_res").innerText = "Errore di rete.";
                return;
            }

            let temperatures = trimTemperaturesNonZero(JSON.parse(this.responseText));

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
                            hidden: true,
                            cubicInterpolationMode: 'monotone',
                            tension: 0.4
                        },
                        { 
                            data: temperatures["heatingCircuits"][1],
                            label: "Piano 1",
                            borderColor: "#f3622d",
                            backgroundColor: "#f3622d",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3,
                            cubicInterpolationMode: 'monotone',
                            tension: 0.4
                        },
                        { 
                            data: temperatures["heatingCircuits"][2],
                            label: "Piano 2",
                            borderColor: "#fbab25",
                            backgroundColor: "#fbab25",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3,
                            cubicInterpolationMode: 'monotone',
                            tension: 0.4
                        },
                        { 
                            data: temperatures["heatingCircuits"][3],
                            label: "Piano 3",
                            borderColor: "#57b757",
                            backgroundColor: "#57b757",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 3,
                            pointHoverRadius: 3,
                            cubicInterpolationMode: 'monotone',
                            tension: 0.4
                        },
                        { 
                            data: temperatures["boilerTemperatures"],
                            label: "Acqua sanitaria ",
                            borderColor: "#1e3aa7",
                            backgroundColor: "#1e3aa7",
                            fill: false,
                            borderWidth: 2.5,
                            pointRadius: 3,
                            pointHoverRadius: 3,
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
                                text: 'Temperatura - °C'
                            },
                            grid: {
                                color: "#7F7F7F"
                            },
                            border: {
                                dash: [8, 4]
                            },
                            ticks: {
                                count: 6
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
    var year = document.getElementById("anno").value;
    var month = document.getElementById("mese").value;
    
    if (month < 10) { // fix mesi senza 0 davanti
        month = "0" + month;
    }

    var date = year + "-" + month;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){
            if (this.responseText.toString() == "0" || this.responseText.toString() == "-1"){
                $('#errormodal').modal('show');
                document.getElementById("error_res").innerText = "Nessun dato trovato per il mese selezionato.";
                return;
            }

            let consumedEnergy = JSON.parse(this.responseText)
            
            // total monthly consumed energy
            let totalMonthlyConsumed = 0;
            for (let i = 0; i < consumedEnergy.measure.length; i++) {
                totalMonthlyConsumed += consumedEnergy.measure[i];
            }
            document.getElementById("totalMonthlyConsumed").innerText = `Consumo totale: ${totalMonthlyConsumed} kWh`
            
            // average consumed energy
            let monthlyAverage = 0;
            consumedEnergy.measure.forEach(function (num) { monthlyAverage += num });
            
            let today = new Date();
            if (today.getFullYear() == year && ('0' + (today.getMonth() + 1)).slice(-2) == month){
                monthlyAverage = monthlyAverage / (today.getDate() - 1);
            }else{
                monthlyAverage = monthlyAverage / consumedEnergy.measure.length;
            }
            
            

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
                            borderColor: "rgba(100, 100, 100, 1.0)",
                            backgroundColor: "rgba(200, 200, 200, 1.0)",
                            borderWidth: 2.3,
                            barPercentage: 1.0
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
                            },
                            grid: {
                                color: "#7F7F7F"
                            },
                            border: {
                                dash: [8, 4]
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Consumo energetico- kW/h'
                            },
                            grid: {
                                color: "#7F7F7F"
                            },
                            border: {
                                dash: [8, 4]
                            },
                            ticks: {
                                count: 6
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
                                        display: true,
                                        content: `Media: ${Math.round(monthlyAverage * 100) / 100} kW`,
                                        backgroundColor: "transparent",
                                        color: 'rgb(255, 99, 132)',
                                        position: "end",
                                        yAdjust: -12,
                                        textStrokeColor: '#FFFFFF', 
                                        textStrokeWidth: 5, 
                                        font: {
                                            size: 14,
                                        }
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
            if (this.responseText.toString() == "-1"){
                $('#errormodal').modal('show');
                document.getElementById("error_res").innerText = "Nessun dato trovato per il mese selezionato.";
                return;
            }
            let data = JSON.parse(this.responseText)
            
            document.getElementById("temperaturaEsterna").innerText = data["temperaturaEsterna"] + " °C";
            document.getElementById("modulazionePompa").innerText = data["modulazionePompa"] + " %";
            document.getElementById("temperaturaMandata").innerText = data["temperaturaMandata"] + " °C";
            document.getElementById("setpointAttuale").innerText = data["setpointAttuale"] + " °C";
            document.getElementById("temperaturaAttuale").innerText = data["temperaturaAttuale"] + " °C";
            
            // creazione tabella circuiti di riscaldamento
            let setPointAmbienteRow = document.getElementById("setPointAmbiente");
            let temperaturaAmbienteRow = document.getElementById("temperaturaAmbiente");
            let temperaturaMandataHcRow = document.getElementById("temperaturaMandataHc");
            
            // hc parte da 2 in quanto non siamo interessati a hc 1 (piano 0)
            for (let hc = 1; hc < data["temperatureHc"]["setPointAmbiente"].length; hc++) {

                let valSetPointAmbiente = document.createElement("td");
                let valtemperaturaAmbiente = document.createElement("td");
                let valtemperaturaMandata = document.createElement("td");

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