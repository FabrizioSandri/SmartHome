let dailyConsumedEnergyChart;
let monthlyConsumedEnergyChart;
let dailyTemperaturesChart;

function getConsumedEnergy() {
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

            // se il grafico esisteva gia lo distruggo e poi ricreo
            if (dailyConsumedEnergyChart) { 
                dailyConsumedEnergyChart.destroy();
            }
            
            dailyConsumedEnergyChart = new Chart("energyConsumed-chart", {
                type: 'line',
                data: {
                    labels: consumedEnergy.hours,
                    datasets: [
                        { 
                            data: consumedEnergy.measure,
                            label: "Consumo energetico",
                            fill: true,
                            borderColor: "#2c3e50",
                            backgroundColor: "rgba(44, 62, 80, 0.4)"
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    scales: {
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Orario'
                            }
                        }],
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Consumo - kW/h'
                            },
                            ticks: {
                                beginAtZero: true,
                                max: Math.max.apply(null, consumedEnergy.measure) + 0.5
                            }
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            title: function(tooltipItem){
                                return "Orario: " + this._data.labels[tooltipItem[0].index];
                            },
                            label: (tooltipItems, data) => {
                                return "Consumo: " + data.datasets[tooltipItems.datasetIndex].data[tooltipItems.index] + ' kW';
                            }
                        }
                    } 
                }
            });
            
        }
    }
    
    xhttp.open("GET", "buderus/energyConsumed?date=" + date, true);
    xhttp.send();
}

function getTemperatures() {
    date = document.getElementById("day").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200){

            temperatures = JSON.parse(this.responseText);
            
            // se il grafico esisteva gia lo distruggo e poi ricreo
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
                            fill: true
                        },
                        { 
                            data: temperatures["heatingCircuits"][1],
                            label: "piano 1",
                            borderColor: "#b85042",
                            fill: true
                        },
                        { 
                            data: temperatures["heatingCircuits"][2],
                            label: "piano 2",
                            borderColor: "#adcbe3",
                            fill: true
                        },
                        { 
                            data: temperatures["heatingCircuits"][3],
                            label: "piano 3",
                            borderColor: "#5e6aa7",
                            fill: true
                        },
                        { 
                            data: temperatures["boilerTemperatures"],
                            label: "Acqua sanitaria ",
                            borderColor: "#1e3aa7",
                            fill: true
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    scales: {
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Orario'
                            }
                        }],
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Temperatura - °C'
                            }
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            title: function(tooltipItem){
                                return "Orario: " + this._data.labels[tooltipItem[0].index];
                            },
                            label: (tooltipItems, data) => {
                                return "Temperatura: " + data.datasets[tooltipItems.datasetIndex].data[tooltipItems.index] + ' °C';
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
    getConsumedEnergy();
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
            
            // se il grafico esisteva gia lo distruggo e poi ricreo
            if (monthlyConsumedEnergyChart) { 
                monthlyConsumedEnergyChart.destroy();
            }
            
            monthlyConsumedEnergyChart = new Chart("energyConsumedMonthly-chart", {
                type: 'line',
                data: {
                    labels: consumedEnergy.days,
                    datasets: [
                        { 
                            data: consumedEnergy.measure,
                            label: "Consumo energetico",
                            fill: true,
                            borderColor: "#2c3e50",
                            backgroundColor: "rgba(44, 62, 80, 0.4)"
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    scales: {
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Giorno'
                            }
                        }],
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Consumo energetico- kW/h'
                            }
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            title: function(tooltipItem){
                                return "Giorno del mese: " + this._data.labels[tooltipItem[0].index];
                            },
                            label: (tooltipItems, data) => {
                                return "Consumo: " + data.datasets[tooltipItems.datasetIndex].data[tooltipItems.index] + ' kW';
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