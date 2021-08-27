console.log("Its alive");
var base_url='http://127.0.0.1:5000';
// var base_url='http://real-state-env.eba-putiyphn.us-east-2.elasticbeanstalk.com';

var accuracy_value;
var canvasBar;
var test;
var state;
var min_price;
var max_price;
var min_surface;
var max_surface;
var min_rooms;
var max_rooms;
var min_enviroments;
var max_enviroments;

var postal_code;
var total_surface;
var rooms;
var bathrooms;
var constructed_surface;
var parking_lots;

// Function that returns Canvas of Bar Chart
function BarChartCanvas(id, category, streams, bar_color){
    var ctx = document.getElementById(id).getContext('2d');
    canvasBar = new Chart(ctx, {
        type: 'bar',
        data: {
            // labels: first(10,category),
            labels: category,
            datasets: [{data: streams, 
                label: 'Model Weight', 
                backgroundColor: [bar_color], 
                borderWidth: 2,	
                datalabels:{
                    anchor:'end',
                    align:'top',
                    font:{
                        weight:'bolder',
                        size:14
                    }

                }
            }]
        },
        plugins: [ChartDataLabels],
        options: {
            legend:{
                display:false
            },
            scales: {
                y: {
                    display: true,
                    title: {text:"Importance", display:true, color:'black', font: {size: 16, family:"Poppins",weight:"bold"}},
                    ticks: {color : 'gray', font: {family:"Poppins"}},
                },
                // x: {
                //     display: true,
                //     title: {text: "Features", display:true, color:'black', font: {size: 16, family:"Poppins",weight:"bold"}},
                //     ticks: {color : 'gray', font: {family:"Poppins"}},
                // },
            },
            plugins:{   
                legend: {
                display: false
                        },
                    }
            // plugins: {legend: {display:true, labels:{color:'black',font: {family:"Poppins"}}}}
        }
    });
    return canvasBar
}
// Function that plots 4 Box Charts
function BoxChartCanvas(){
    d3.json(base_url+'/boxes?State='+ state + '&Min_price=' + min_price + '&Max_price=' + max_price
    + '&Min_surface=' + min_surface + '&Max_surface=' + max_surface 
    + '&Min_rooms=' + min_rooms + '&Max_rooms=' + max_rooms 
    + '&Min_enviroments=' + min_enviroments + '&Max_enviroments=' + max_enviroments).then(importedData=>{
    data=importedData

    box_prices = data.map(sample=>sample.box_price)[0]
    box_surfaces = data.map(sample=>sample.box_surface)[0]
    box_rooms = data.map(sample=>sample.box_room)[0]
    box_enviroments = data.map(sample=>sample.box_enviroment)[0]

    BoxChart('boxplot_prices', box_prices)
    BoxChart('boxplot_surface', box_surfaces)
    BoxChart('boxplot_room', box_rooms)
    BoxChart('boxplot_enviroment', box_enviroments)

})
}
// Function that draws an individual Box Chart
function BoxChart(id, box_data){
    // var trace1 = {y: box_data, type: 'box', boxpoints:'all',jitter:0.1,pointspos:-1.8};
    var trace1 = {y: box_data, type: 'box', boxpoints:'all', marker: {color: '#3b7ddd'},};
    // var trace1 = {y: box_data, type: 'box'};
    var data = [trace1];
    var layout = {
        autosize: false,
        width: 340,
        height: 200,
        margin: {
          l: 80,
        //   r: 50,
          b: 0,
          t: 0,
          pad: 0
        },
      };
    Plotly.newPlot(id, data, layout);
}
// Function that crates end point params
function query_params(){
    return 'State='+ state + '&Min_price=' + min_price + '&Max_price=' + max_price + '&Min_surface=' + min_surface + '&Max_surface=' + max_surface + '&Min_rooms=' + min_rooms + '&Max_rooms=' + max_rooms + '&Min_enviroments=' + min_enviroments + '&Max_enviroments=' + max_enviroments 
}

function predict_params(){
    return '&postal_code=' + postal_code + '&type=' + type + '&enviroments=' + enviroments + '&rooms=' + rooms + '&bathrooms=' + bathrooms + '&constructed_surface=' + constructed_surface + '&parking_lots=' + parking_lots 
}

// Fill dropdowns when page loads
d3.json(base_url+'/dropdowns?').then(importedData=>{
    data=importedData
    var states = ((data.map(sample=>sample.states))[0]).sort();
    
    states.forEach(state=>{d3.select("#state_selector").append("option").classed("dropdown-item",true).style("value",state).text(state)}) 
})

// Listener that updates model when any filter changes
d3.selectAll(".form-state").on("change", updateModel);
d3.selectAll("#filter_button").on("click", updateModel);

function updateModel() {
    console.log("Updating Model...")
    test = d3.select("#state_selector").property("value")
    console.log("En model: " + test)

    state = d3.select("#state_selector").property("value")
    min_price = d3.select("#min_price").property("value")
    max_price = d3.select("#max_price").property("value")
    min_surface = d3.select("#min_surface").property("value")
    max_surface = d3.select("#max_surface").property("value")
    min_rooms = d3.select("#min_rooms").property("value")
    max_rooms = d3.select("#max_rooms").property("value")
    min_enviroments = d3.select("#min_enviroments").property("value")
    max_enviroments = d3.select("#max_enviroments").property("value")

    d3.json(base_url+'/results?'+ query_params()).then(importedData=>{
    
        var data = importedData
        console.log(data)

        accuracy_value = data.accuracy+"%"

        d3.select("#MAE").text(new Intl.NumberFormat('en-US', { style: 'currency', currency: 'MXN' }).format(data.mae))
        d3.select("#MAPE").text(data.mape+"%")
        d3.select("#ACCURACY").text(data.accuracy+"%") 
        d3.select("#RMSE").text(new Intl.NumberFormat('en-US', { style: 'currency', currency: 'MXN' }).format(data.rmse))
        d3.select("#state_selected").text("Prediction based on " + test + " data")
        
        var features_lst = []
        var weight_lst = []

        for (var i in data.features_importance.Features){
            features_lst.push(data.features_importance.Features[i])
        }

        for (var i in data.features_importance.Importance){
            weight_lst.push(data.features_importance.Importance[i])
        }

        if (canvasBar){canvasBar.destroy()}
        BarChartCanvas("features_by_importance",features_lst,weight_lst,'rgba(59, 125, 221, 1)')
        
    })
    BoxChartCanvas()
}


// ########################################################################################################################
// Predictions

// Listener that updates model when any filter changes
d3.selectAll(".form-type").on("change", predictModel);
d3.selectAll("#predict_button").on("click", predictModel)

function predictModel() {
    console.log("Predicting Model...")
    console.log("En predict: " + test)
    
    type = d3.select("#property_selector").property("value")
    state = d3.select("#state_selector").property("value")
    postal_code = d3.select("#cp_selector").property("value")
    enviroments = d3.select("#enviroments").property("value")
    rooms = d3.select("#rooms").property("value")
    bathrooms = d3.select("#bathrooms").property("value")
    constructed_surface = d3.select("#cons_surface").property("value")
    parking_lots = d3.select("#parking_lots").property("value")
    
    
    d3.json(base_url+'/prediction?'+ query_params() + predict_params()).then(importedData=>{
        var data = importedData

        prediction = data.map(sample=>sample.Prediction) 
        prediction = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'MXN' }).format(prediction)

        d3.select("#predicted_value").text(prediction)
        d3.select("#accuracy_value").text(accuracy_value)        
    })

}