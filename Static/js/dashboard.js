// d3.json("http://127.0.0.1:5000/songs").then((importedData)=>{
//     var songs = importedData;
//     console.log(songs);
// });

var canvasLine;
var canvasBarArtist;
var canvasBarTrack;
var canvasBarCountry;
var canvasDonut;


// Function to create a bar Chart
function barChart(group_by,country,artist,track,datefrom,dateto,xAxisTitle,id,bar_color){
    d3.json('http://127.0.0.1:5000/songs?Group_by='+ group_by + '&Country=' + country + '&Artist=' + artist + '&Track_Name=' + track + '&datefrom='+ datefrom + '&dateto=' + dateto).then(importedData=>{
    var data = importedData;
    var category = data.map(sample=>sample[group_by]);
    var streams = data.map(sample=>sample.Streams);
    // Chart.js ---------------------------------------------------------
    if(group_by==="Artist"){
        canvasBarArtist = BarChartCanvas(id,category,streams,xAxisTitle,bar_color);
    }
    if(group_by==="Track_Name"){
        canvasBarTrack = BarChartCanvas(id,category,streams,xAxisTitle,bar_color);
    }
    if(group_by==="Country"){
        canvasBarCountry = BarChartCanvas(id,category,streams,xAxisTitle,bar_color);
    }
});
}

// Function that returns Canvas of Bar Chart
function BarChartCanvas(id,category,streams,xAxisTitle,bar_color){
    var ctx = document.getElementById(id).getContext('2d');
    canvasBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: first(10,category),
            datasets: [{data: streams, label: '# of Streams', backgroundColor: [bar_color], borderWidth: 2}]
        },
        options: {
            scales: {
                y: {
                    display: true,
                    title: {text:"Streams", display:true, color:'white', font: {size: 16, family:"Poppins",weight:"bold"}},
                    ticks: {color : 'white', font: {family:"Poppins"}},
                },
                x: {
                    display: true,
                    title: {text: xAxisTitle, display:true, color:'white', font: {size: 16, family:"Poppins",weight:"bold"}},
                    ticks: {color : 'white', font: {family:"Poppins"}},
                },
            },
            plugins: {legend: {display:true, labels:{color:'white',font: {family:"Poppins"}}}}
        }
    });
    return canvasBar
}

// Function to create a line Chart
function lineChart(group_by,country,artist,track,datefrom,dateto,xAxisTitle,id) {
    d3.json('http://127.0.0.1:5000/streamsbydate?Group_by='+ group_by + '&Country=' + country + '&Artist=' + artist + '&Track_Name=' + track + '&datefrom='+ datefrom + '&dateto=' + dateto).then(importedData=>{
    var data = importedData;

    var category = data.map(sample=>sample[group_by]);
    var streams = data.map(sample=>sample.Streams);

    const totalDuration = 5000;
    const delayBetweenPoints = totalDuration / data.length;
    const previousY = (ctx) => ctx.index === 0 ? ctx.chart.scales.y.getPixelForValue(100) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
    const animation = {
      x: {
        type: 'number',
        easing: 'linear',
        duration: delayBetweenPoints,
        from: NaN, // the point is initially skipped
        delay(ctx) {
          if (ctx.type !== 'data' || ctx.xStarted) {
            return 0;
          }
          ctx.xStarted = true;
          return ctx.index * delayBetweenPoints;
        }
      },
      y: {
        type: 'number',
        easing: 'linear',
        duration: delayBetweenPoints,
        from: previousY,
        delay(ctx) {
          if (ctx.type !== 'data' || ctx.yStarted) {
            return 0;
          }
          ctx.yStarted = true;
          return ctx.index * delayBetweenPoints;
        }
      }
    };



    // Chart.js ---------------------------------------------------------
    var ctx = document.getElementById(id).getContext('2d');
    
        canvasLine = new Chart(ctx, {
        type: 'line',
        data: {
            labels: first(30,category),
            datasets: [{data: streams, label: '# of Streams', backgroundColor: ['rgba(30, 215, 96, 1)'], borderColor: ['rgba(30, 215, 96, 1)'], borderWidth: 2}]
        },
        options: {
            animation,
            interaction: {
              intersect: false
            },
            scales: {
                y: {
                    display: true,
                    title: {text:"Streams", display:true, color:'white', font: {size: 16, family:"Poppins",weight:"bold"}},
                    ticks: {color : 'white', font: {family:"Poppins"}},
                },
                x: {
                    display: true,
                    title: {text: xAxisTitle, display:true, color:'white', font: {size: 16, family:"Poppins",weight:"bold"}},
                    ticks: {color : 'white', font: {family:"Poppins"}},
                },
            },
            plugins: {legend: {display:true, labels:{color:'white',font: {family:"Poppins"}}}},
            maintainAspectRatio: false,
        }
    });    
});
    // return canvas
}

// Function to create a donut Chart
function donutChart(group_by,country,artist,track,datefrom,dateto,id){
    d3.json('http://127.0.0.1:5000/songs?Group_by='+ group_by + '&Country=' + country + '&Artist=' + artist + '&Track_Name=' + track + '&datefrom='+ datefrom + '&dateto=' + dateto).then(importedData=>{
        // console.log(importedData)

        var data = importedData;
        var category = data.map(sample=>sample[group_by]);
        var streams = data.map(sample=>sample.Streams);
        // Chart.js ---------------------------------------------------------
        var ctx = document.getElementById(id).getContext('2d');
            canvasDonut = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: first(3,category),
                    datasets: [{
                        label: '# of Streams',
                        data: first(3,streams),
                        backgroundColor: ['rgba(30, 215, 96, 1)','rgba(66, 133, 244,1)','rgba(219, 68, 55,1)'],
                        borderColor: ['rgba(25, 28, 36, 1)'],
                        borderWidth: 10
                    }],
                    hoverOffset: 4
                },
                options:{
                    plugins: {legend: {display:true, labels:{color:'white',font: {family:"Poppins", size:16}}}}
                }
            
            });
    });
}

// Function to Filter a JSON to n elements of it
function first(x,data) {
    data = data.slice(0, x)
    return data
};

//Welcome to the Spotify Dash 
console.log("Its working :D")

// Initial Setup without Filters
var country = ""
var artist= ""
var track = ""
var datefrom = ""
var dateto = ""

d3.json('http://127.0.0.1:5000/summary?Country=' + country + '&Artist=' + artist + '&Track_Name=' + track + '&datefrom='+ datefrom + '&dateto=' + dateto).then(importedData=>{
    // console.log(importedData)
    var data = importedData;

    var Artist_Count = data.map(sample=>sample.ArtistCount);
    var Songs_Count = String(data.map(sample=>sample.SongsCount)).replace(/(.)(?=(\d{3})+$)/g,'$1,');
    var Total_Streams = String(data.map(sample=>sample.TotalStreams)).replace(/(.)(?=(\d{3})+$)/g,'$1,');

    d3.select("#country_selected").text("Global")
    d3.select("#artist_count").text(Artist_Count)
    d3.select("#songs_count").text(Songs_Count)
    d3.select("#total_streams").text(Total_Streams)

    var countries = ((data.map(sample=>sample.Countries))[0]).sort();
    var artists = ((data.map(sample=>sample.Artists))[0]).sort();
    var songs = ((data.map(sample=>sample.Songs))[0]).sort();

    // Adding array elements to dropdowns
    countries.forEach(country=>{d3.select("#country_selector").append("option").classed("dropdown-item",true).style("value",country).text(country)})
    artists.forEach(artist=>{d3.select("#artist_selector").append("option").classed("dropdown-item",true).style("value",artist).text(artist)})
    songs.forEach(track=>{d3.select("#song_selector").append("option").classed("dropdown-item",true).style("value",track).text(track)})
});

// Chart Function Parameters:
// 1.group_by,
// 2.[Filters]
// 3.X Axis Title
// 4.HTML id for select 
// 5.Name of Canvas that occupies the chart
// 6.Color of Bars)

// Initial Charts Run
// LineChart
// canvas = 'LineChart'
lineChart("MonthYear",country,artist,track,datefrom,dateto,"Month of the Year","StreamsByDateChart")
// ChartByGenre
donutChart("Genre",country,artist,track,datefrom,dateto,"StreamsByGenre")
// BarCharts
barChart("Artist",country,artist,track,datefrom,dateto,"Top Artist","StreamsByArtistPlot",'rgba(30, 215, 96, 1)')
barChart("Track_Name",country,artist,track,datefrom,dateto,"Top Songs","StreamsByTrackPlot",'rgb(29, 117, 222, 1)')
barChart("Country",country,artist,track,datefrom,dateto,"Top Countries","StreamsByCountryPlot",'rgb(255, 153, 0, 1)')

d3.selectAll(".form-control").on("change", updateDashboard);

// ----------------------------------------------------------------------------------------------------------------------------------------

function updateDashboard() {
    // Retrieve Selectors
    if (country === ""){country="Global"}else{var country = d3.select("#country_selector").property("value")}

    var artist= d3.select("#artist_selector").property("value")
    var track = d3.select("#song_selector").property("value")

    try {var datefrom = d3.select("#begin_selector").property("value")} catch(error){var datefrom = ""}
    try {var dateto = d3.select("#end_selector").property("value")} catch(error){var dateto = ""}
    
    // Function that updates line chart 
    canvasLine.destroy()
    lineChart("MonthYear",country,artist,track,datefrom,dateto,"Month of the Year","StreamsByDateChart")
    
    canvasDonut.destroy()
    donutChart("Genre",country,artist,track,datefrom,dateto,"StreamsByGenre")

    canvasBarArtist.destroy()
    barChart("Artist",country,artist,track,datefrom,dateto,"Top Artist","StreamsByArtistPlot",'rgba(30, 215, 96, 1)')

    canvasBarTrack.destroy()
    barChart("Track_Name",country,artist,track,datefrom,dateto,"Top Songs","StreamsByTrackPlot",'rgb(29, 117, 222, 1)')

    canvasBarCountry.destroy()
    barChart("Country",country,artist,track,datefrom,dateto,"Top Countries","StreamsByCountryPlot",'rgb(255, 153, 0, 1)')
    
    d3.json('http://127.0.0.1:5000/summary?Country=' + country + '&Artist=' + artist + '&Track_Name=' + track + '&datefrom='+ datefrom + '&dateto=' + dateto).then(importedData=>{
        var data = importedData;

        var Artist_Count = data.map(sample=>sample.ArtistCount);
        var Songs_Count = String(data.map(sample=>sample.SongsCount)).replace(/(.)(?=(\d{3})+$)/g,'$1,');
        var Total_Streams = String(data.map(sample=>sample.TotalStreams)).replace(/(.)(?=(\d{3})+$)/g,'$1,');

        if (country===""){country="Global"}
        d3.select("#country_selected").text(country)
        d3.select("#artist_count").text(Artist_Count)
        d3.select("#songs_count").text(Songs_Count)
        d3.select("#total_streams").text(Total_Streams)

        var countries = ((data.map(sample=>sample.Countries))[0]).sort();
        var artists = ((data.map(sample=>sample.Artists))[0]).sort();
        var songs = ((data.map(sample=>sample.Songs))[0]).sort();
        
        // Adding array elements to dropdowns
        if(d3.select("#country_selector").property("value") == ""){
            d3.select("#country_selector").html("")
            countries.forEach(country=>{d3.select("#country_selector").append("option").classed("dropdown-item",true).style("value",country).text(country)})
        } 
        if(d3.select("#artist_selector").property("value") == ""){
            d3.select("#artist_selector").html("")
            artists.forEach(artist=>{d3.select("#artist_selector").append("option").classed("dropdown-item",true).style("value",artist).text(artist)})
        } 
        if(d3.select("#song_selector").property("value") == ""){
            d3.select("#song_selector").html("")
            songs.forEach(track=>{d3.select("#song_selector").append("option").classed("dropdown-item",true).style("value",track).text(track)})
        }        
    });

} // The function that updates the Dashboard ends











