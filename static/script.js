function byId(id) {
    return document.getElementById(id);
}

function getData(id) {
    return byId(id).textContent.split(',');
}

var default_options = {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero:true
            }
        }]
    }
}

var defaultBackgroundColors = [
    'rgba(255, 99, 132, 0.8)',
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)'
]

var defaultBorderColors = [
    'rgba(255,99,132,1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)'
]

var transparentColor = 'rgb(0, 0, 0, 0.0)';


var totalCtx = byId("totalChart").getContext('2d');

var current = getData("current");
var previous = getData("previous");
var estimate = getData("estimate");

var totalChart = new Chart(totalCtx, {
    type: 'bar',
    data: {
        labels: ["Previous", "Current", "Estimate"],
        datasets: [{
            label: 'Expenses',
            backgroundColor: [
                defaultBackgroundColors[0],
                defaultBackgroundColors[1],
                defaultBackgroundColors[1].replace('0.8', '0.5')
            ],
            borderColor: defaultBorderColors,
            data: [previous, current, estimate],
        }]
    },
    options: default_options
});


var byTypeCtx = byId("byTypeChart").getContext('2d');

var current_by_type = getData("current_by_type");
var previous_by_type = getData("previous_by_type");
var estimates_by_type = getData("estimates_by_type");
var types = getData("types");

var estimateColors = defaultBackgroundColors.slice();
for (var i = 0; i < estimateColors.length; i++) {
    estimateColors[i] = estimateColors[i].replace('0.8', '0.5')
}

var byTypeChart = new Chart(byTypeCtx, {
    type: 'bar',
    data: {
        labels: types,
        datasets: [{
            label: 'Previous',
            backgroundColor: defaultBackgroundColors,
            borderColor: defaultBorderColors,
            data: previous_by_type,
        },
        {
            label: 'Current',
            backgroundColor: defaultBackgroundColors,
            borderColor: defaultBorderColors,
            data: current_by_type,
        },
        {
            label: 'Estimate',
            backgroundColor: estimateColors,
            borderColor: defaultBorderColors,
            data: estimates_by_type,
        }]
    },
    options: default_options
});


var dailyCtx = byId("dailyChart").getContext('2d');

var days = [];
for (var i = 1; i < 32; i++) {
    days.push(i);
}

var current_daily = getData("current_daily");
var previous_daily = getData("previous_daily");

var dailyChart = new Chart(dailyCtx, {
    type: 'line',
    data: {
        labels: days,
        datasets: [{
                label: 'Previous',
                backgroundColor: transparentColor,
                borderColor: defaultBorderColors[0],
                data: previous_daily,
            },
            {
            label: 'Current',
            backgroundColor: transparentColor,
            borderColor: defaultBorderColors[1],
            data: current_daily,
        }]
    },
    options: default_options
});
