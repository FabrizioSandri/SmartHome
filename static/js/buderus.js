let dailyConsumedEnergyChart;
let monthlyConsumedEnergyChart;
let dailyTemperaturesChart;

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
            
            dailyConsumedEnergyChart = new Chart("energyConsumed-chart", {
                type: 'bar',
                data: {
                    labels: consumedEnergy.hours,
                    datasets: [
                        { 
                            data: consumedEnergy.measure,
                            label: "Consumo energetico",
                            borderColor: "black",
                            backgroundColor: "rgba(44, 62, 80, 0.4)",
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }
                    ]
                },
                options: {
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
                                text: 'Consumo - kW/h'
                            },
                            ticks: {
                                beginAtZero: true,
                                max: Math.max.apply(null, consumedEnergy.measure) + 0.5
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function(TooltipItems){
                                    return "Orario: " + TooltipItems[0].label ;
                                },
                                label: (TooltipItem) => {
                                    return "Consumo: " + TooltipItem.formattedValue + ' kW';
                                }
                            }
                        }
                    }
                    
                }
            });
            
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
                type: 'line',
                data: {
                    labels: temperatures.hours,
                    datasets: [
                        { 
                            data: temperatures["heatingCircuits"][0],
                            label: "HC1",
                            borderColor: "#0e9aa7",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            hidden: true
                        },
                        { 
                            data: temperatures["heatingCircuits"][1],
                            label: "Piano 1",
                            borderColor: "#f3622d",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        { 
                            data: temperatures["heatingCircuits"][2],
                            label: "Piano 2",
                            borderColor: "#fbab25",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        { 
                            data: temperatures["heatingCircuits"][3],
                            label: "Piano 3",
                            borderColor: "#57b757",
                            fill: false,
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        { 
                            data: temperatures["boilerTemperatures"],
                            label: "Acqua sanitaria ",
                            borderColor: "#1e3aa7",
                            fill: false,
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }
                    ]
                },
                options: {
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
                            callbacks: {
                                title: function(TooltipItems){
                                    return `Ore ${TooltipItems[0].label} - ${TooltipItems[0].dataset.label}`;
                                },
                                label: (TooltipItem) => {
                                    return "Temperatura: " + TooltipItem.formattedValue + ' °C';
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
                            borderColor: "black",
                            backgroundColor: "rgba(44, 62, 80, 0.4)",
                            borderWidth: 2.2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                        }
                    ]
                },
                options: {
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