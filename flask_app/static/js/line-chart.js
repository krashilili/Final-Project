var url = `/date_added`;

sucess = function(data) {
    console.log(data);
    // Build line chart
    var trace1 = {
        x: data.dates,
        y: data.jobs_available,
        type: "line"
    };
    var data = [trace1];
    var layout = {
        title: `Available Jobs`,
        xaxis: { title: ""},
        yaxis: { title: "Number of Jobs"}
    };
    Plotly.newPlot("line", data, layout);   
    
};

d3.json(url, sucess);

    
