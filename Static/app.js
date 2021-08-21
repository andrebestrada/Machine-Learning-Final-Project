
// d3.json("http://127.0.0.1:5000/songs").then((importedData)=>{
//     var songs = importedData;
//     console.log(songs);

// });

console.log("Its working")

d3.request("http://google.com").get(importedData=>{
    var songs = importedData;
    console.log(songs);
    
    console.log("Its alive")
});