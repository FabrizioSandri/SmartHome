function displayCharts(chartData) {
    
    new Chart("wind-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["windSpeed"],
                    label: "Velocità vento (km/h)",
                    borderColor: "#0e9aa7",
                    fill: true
                }
            ]
        },
        options: {
            title: {
                display: true,
            },
            scales: {
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 10
                    }
                }]
            },
            maintainAspectRatio: false,
        }
    });
    
    new Chart("temp-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["outTemp"],
                    label: "Temperatura esterna (°C)",
                    borderColor: "#fe8a71",
                    fill: true
                },
                { 
                    data: chartData.data["inTemp"],
                    label: "Temperatura interna (°C)",
                    borderColor: "#adcbe3",
                    fill: true
                }
            ]
        },
        options: {
            title: {
                display: true,
            },
            scales: {
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 10
                    }
                }]
            },
            maintainAspectRatio: false,
        }
    });

    new Chart("barometer-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["barometer"],
                    label: "Pressione atmosferica (hPa)",
                    borderColor: "#f6cd61",
                    fill: true
                }
            ]
        },
        options: {
            title: {
                display: true,
            },
            scales: {
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 10
                    }
                }]
            },
            maintainAspectRatio: false,
        }
    });

    new Chart("humidity-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["outHumidity"],
                    label: "Umidità esterna (%)",
                    borderColor: "#fe8a71",
                    fill: true
                },
                { 
                    data: chartData.data["inHumidity"],
                    label: "Umidità interna (%)",
                    borderColor: "#adcbe3",
                    fill: true
                }
            ]
        },
        options: {
            title: {
                display: true,
            },
            scales: {
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 10
                    }
                }]
            },
            maintainAspectRatio: false,
        }
    });

    new Chart("rain-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["dayRain"],
                    label: "Pioggia totale (cm)",
                    borderColor: "#4E342E",
                    fill: true
                }
            ]
        },
        options: {
            title: {
                display: true,
            },
            scales: {
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 10
                    }
                }]
            },
            maintainAspectRatio: false,
        }
    });

}

