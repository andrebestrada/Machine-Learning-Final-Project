
function scatterplot(TopChartData,x,y,id,color_circle){
  titlex=x
  titley=y
  
  y=TopChartData.map(sample=>sample[y])
  x=TopChartData.map(sample=>sample[x])

  ArtistName=TopChartData.map(sample=>sample['Artist Name'])            
  Song=TopChartData.map(sample=>sample['Track Name'])
  TraceTitle = TopChartData.map(sample=>"<b>Artist</b>: "+sample['Artist Name']+"<br><b>Track:</b> "+sample['Track Name'])

  var trace1 = {x: x, y: y,
    hovertemplate: '%{text}<extra></extra>',
    text: TraceTitle,
    showlegend: false,
    mode: 'markers', 
    type: 'scatter',
    marker: {
      size:10,
      color:color_circle
    }
  };
  
  var layout = {
    paper_bgcolor:'rgba(0,0,0,0)',
    plot_bgcolor:'rgba(0,0,0,0)',
    title: {
      text: `${titlex} vs ${titley}`,
      font: {family: 'Poppins, monospace', size: 22, color: 'white'}
    },
    xaxis: {
      gridwidth: 0.1,
      title: {
        text: titlex,
        font: {family: 'Poppins, monospace', size: 18, color: 'white'}
      },
      tickwidth: 4,
      tickcolor: 'white',
      tickfont:{
        size:14,
        color:'white'
      }

    },
    yaxis: {
      gridwidth: 0.1,
      title: {
        text: titley,
        font: {family: 'Poppins, monospace',size: 18,color: 'white'}
      },
      tickwidth: 4,
      tickcolor: 'white',
      tickfont:{
        size:14,
        color:'white'
      }

    }
  };
  
  var data = [trace1];            
  Plotly.newPlot(id, data,layout);
  

}

d3.json('http://127.0.0.1:5000/Popularity').then(TopChartData=>{
  // console.log(TopChartData)
  scatterplot(TopChartData,'Tempo','Danceability','scatter1','rgba(30, 215, 96, 1)')
  scatterplot(TopChartData,'Danceability','Energy','scatter2','rgb(29, 117, 222, 1)')
  scatterplot(TopChartData,'Energy','Tempo','scatter3','rgb(255, 153, 0, 1)')
  scatterplot(TopChartData,'Liveness','Valence','scatter4','rgba(219, 68, 55,1)')
});