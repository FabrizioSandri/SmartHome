function displayCharts(chartData) {

    new Chart("wind-chart", {
        type: 'custom_line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["windSpeed"],
                    label: "Velocità vento",
                    borderColor: "#1e3aa7",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Velocità vento (km/h)'
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
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
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' km/h';
                        }
                    }
                }
            }
        }
    });
    
    new Chart("temp-chart", {
        type: 'custom_line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["outTemp"],
                    label: "Temperatura esterna",
                    borderColor: "#57b757",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4
                },
                { 
                    data: chartData.data["inTemp"],
                    label: "Temperatura interna",
                    borderColor: "#f3622d",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temperatura (°C)'
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
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
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' °C';
                        }
                    }
                }
            }
        }
    });


    new Chart("barometer-chart", {
        type: 'custom_line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["barometer"],
                    label: "Pressione atmosferica",
                    borderColor: "#fbab25",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Pressione (hPa)'
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
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
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' hPa';
                        }
                    }
                }
            }
        }
    });
    
    new Chart("humidity-chart", {
        type: 'custom_line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["outHumidity"],
                    label: "Umidità esterna",
                    borderColor: "#57b757",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4
                },
                { 
                    data: chartData.data["inHumidity"],
                    label: "Umidità interna",
                    borderColor: "#f3622d",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Umidità (%)'
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
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
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' %';
                        }
                    }
                }
            }
        }
    });


    new Chart("rain-chart", {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                { 
                    data: chartData.data["dayRain"],
                    label: "Pioggia giornaliera",
                    borderColor: "#ef6c00",
                    fill: false,
                    borderWidth: 3.5,
                    pointRadius: 1,
                    pointHoverRadius: 6,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Pioggia (cm)'
                    },
                    beginAtZero: true,
                    grid: {
                        borderDash: [8, 4],
                        color: "#7F7F7F"
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
                            return `Ore ${TooltipItems[0].label}`;
                        },
                        label: (TooltipItem) => {
                            return TooltipItem.dataset.label + ": " + TooltipItem.formattedValue + ' cm';
                        }
                    }
                }
            }
        }
    });

}
