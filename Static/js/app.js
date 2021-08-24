// state='Puebla'
console.log("Its alive")

// Fill dropdowns the page loads
d3.json('http://127.0.0.1:5000/dropdowns').then(importedData=>{
    data=importedData

    var states = ((data.map(sample=>sample.states))[0]).sort();
    
    states.forEach(state=>{d3.select("#state_selector").append("option").classed("dropdown-item",true).style("value",state).text(state)}) 
})

// Listener that updates model when any filter changes
d3.selectAll(".form-control").on("change", updateModel);

function updateModel() {
    console.log("Updating Model...")
    state = d3.select("#state_selector").property("value")

    d3.json('http://127.0.0.1:5000/results?State='+ state).then(importedData=>{
        var data = importedData
        console.log(data)

        d3.select("#MAE").text(data.mae)
        d3.select("#MAPE").text(data.mape)
        d3.select("#ACCURACY").text(data.accuracy+"%") 
        d3.select("#SCORE").text(data.score)


        console.log(data.features_importance.Features)
        console.log(data.features_importance.Importance)
        
        var features_lst = []
        var weight_lst = []

        for (var i in data.features_importance.Features){
            features_lst.push(data.features_importance.Features[i])
        }

        for (var i in data.features_importance.Importance){
            weight_lst.push(data.features_importance.Importance[i])
        }

        console.log(features_lst)
        
        // valores = data.map(sample=>sample.features_importance)
        // console.log(valores)
        
        var dat = [{
            type: 'bar',
            x: weight_lst,
            y: features_lst,
            orientation: 'h'
          }];

          Plotly.newPlot('features_plot', dat);
    })
}