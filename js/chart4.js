// Set the dimensions of the canvas / graph
var chart4margin = {top: 30, right: 20, bottom: 75, left: 50},
    chart4width = parseInt(d3.select('#chart4').style('width')) - chart4margin.left - chart4margin.right,
    chart4height = 600 - chart4margin.top - chart4margin.bottom;

// Set the ranges
var chart4x0 = d3.scale.ordinal().rangeRoundBands([0, chart4width],0.3);
var chart4x1 = d3.scale.ordinal();
var chart4y = d3.scale.linear().range([chart4height, 0]);
var chart4color = d3.scale.ordinal()
      .range(["#4b50af", "#a03030"]);

// Define the axes
var chart4xAxis = d3.svg.axis().scale(chart4x0)
    .orient("bottom");

var chart4yAxis = d3.svg.axis().scale(chart4y)
    .orient("left");

// Adds the svg canvas
var chart4 = d3.select("div#chart4")
    .append("svg")
        .attr("width", chart4width + chart4margin.left + chart4margin.right)
        .attr("height", chart4height + chart4margin.top + chart4margin.bottom)
    .append("g")
        .attr("transform",
              "translate(" + chart4margin.left + "," + chart4margin.top + ")");

// Get the data
var drawGraph = function() {
  d3.csv("output/margins_aggregated.csv", function(error, data) {

      var party = d3.keys(data[0]).filter(function(key) { return key !=='bucket'; });

      data.forEach(function(d) {
        d.margin = party.map(function(name) { return {name: name, value: +d[name]}; });
      });
      // Scale the range of the data
      chart4x0.domain(data.map(function(d) { return d.bucket; }));
      chart4x1.domain(party).rangeRoundBands([0, chart4x0.rangeBand()]);
      chart4y.domain([0, d3.max(data, function(d) { return d3.max(d.margin, function(d) { return d.value; }); })]);

      // Add the X Axis
      chart4.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + chart4height + ")")
          .call(chart4xAxis)
          .selectAll('text')
          .style("text-anchor", "end")
          .attr("dx", "-.3em")
          .attr("dy", (-chart4x1.rangeBand()/2) + 15)
          .attr("transform", function(d) {
              return "rotate(-45)"
          });
      chart4.select('g.x.axis')
        .append('text')
          .attr('dy', 70)
          .attr("dx", chart4width/2)
          .style("text-anchor", "middle")
          .text("Margin of Win (Percentage Points)");

      // Add the Y Axis
      chart4.append("g")
          .attr("class", "y axis")
          .call(chart4yAxis)
        .append('text')
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Count of Elections");

      var category = chart4.selectAll('.category')
          .data(data)
        .enter().append('g')
          .attr('class', 'category')
          .attr("transform", function(d) { return "translate(" + chart4x0(d.bucket) + ",0)"; });

      category.selectAll('rect')
          .data(function(d) { return d.margin; })
        .enter().append('rect')
          .attr("width", chart4x1.rangeBand())
          .attr("x", function(d) { return chart4x1(d.name); })
          .attr("y", function(d) { return chart4y(d.value); })
          .attr("height", function(d) { return chart4height - chart4y(d.value); })
          .style("fill", function(d) { return chart4color(d.name); });

      chart4.append('rect')
          .attr('class', 'iqr_box')
          .attr('x',chart4width*0.75)
          .attr('y',chart4height*0.11)
          .attr('width',200)
          .attr('height',60)
          .attr('rx','8')
          .attr('ry','8');

      d3.json("output/iqr.json", function(error, iqrdata) {

        chart4.append('text')
            .attr('dx', 10)
            .attr('class', 'iqr_text dem')
            .attr('x',chart4width*0.75 + 5)
            .attr('y',chart4height*0.1 + 25)
            .text('Democratic IQR: ' + (iqrdata['all']['D']['0.25']).toFixed(0) + ' to ' + (iqrdata['all']['D']['0.75']).toFixed(0));
        chart4.append('text')
            .attr('dx', 10)
            .attr('class', 'iqr_text rep')
            .attr('x',chart4width*0.75 + 5)
            .attr('y',chart4height*0.1 + 50)
            .text('Republican IQR: ' + (iqrdata['all']['R']['0.25']).toFixed(0) + ' to ' + (iqrdata['all']['R']['0.75']).toFixed(0));

      });
  });
}

var updateGraph = function(year) {
  d3.csv("output/margin_buckets_" + year + ".csv", function(error, data) {
      console.log(data);
      var party = d3.keys(data[0]).filter(function(key) { return key !=='bucket'; });
      data.forEach(function(d) {
        d.margin = party.map(function(name) { return {name: name, value: +d[name]}; });
        console.log(d);
      });

      chart4y.domain([0, d3.max(data, function(d) { return d3.max(d.margin, function(d) { return d.value; }); })]);

      chart4.select('.y.axis')
          .transition().duration(500)
          .call(chart4yAxis);

      var category = chart4.selectAll('.category').data(data);
      var margbars = category.selectAll('rect');

      margbars.data(function(d) { return d.margin; })
          .transition().duration(500)
          .attr("y", function(d) { return chart4y(d.value); })
          .attr("height", function(d) { return chart4height - chart4y(d.value); })
          .style("fill", function(d) { return chart4color(d.name); });

      d3.json("output/iqr.json", function(error, iqrdata) {

        chart4.select('text.iqr_text.dem')
          .text('Democratic IQR: ' + (iqrdata[year]['D']['0.25']).toFixed(0) + ' to ' + (iqrdata[year]['D']['0.75']).toFixed(0));
        chart4.select('text.iqr_text.rep')
          .text('Republican IQR: ' + (iqrdata[year]['R']['0.25']).toFixed(0) + ' to ' + (iqrdata[year]['R']['0.75']).toFixed(0));

      });

  });
}

var redrawGraph = function() {
  d3.csv("output/margins_aggregated.csv", function(error, data) {

      var party = d3.keys(data[0]).filter(function(key) { return key !=='bucket'; });

      data.forEach(function(d) {
        d.margin = party.map(function(name) { return {name: name, value: +d[name]}; });
      });

      chart4y.domain([0, d3.max(data, function(d) { return d3.max(d.margin, function(d) { return d.value; }); })]);

      chart4.select('.y.axis')
          .transition().duration(500)
          .call(chart4yAxis);

      var category = chart4.selectAll('.category').data(data);
      var margbars = category.selectAll('rect');

      margbars.data(function(d) { return d.margin; })
          .transition().duration(500)
          .attr("y", function(d) { return chart4y(d.value); })
          .attr("height", function(d) { return chart4height - chart4y(d.value); })
          .style("fill", function(d) { return chart4color(d.name); });

      d3.json("output/iqr.json", function(error, iqrdata) {

        chart4.select('text.iqr_text.dem')
          .text('Democratic IQR: ' + (iqrdata['all']['D']['0.25']).toFixed(0) + ' to ' + (iqrdata['all']['D']['0.75']).toFixed(0));
        chart4.select('text.iqr_text.rep')
          .text('Republican IQR: ' + (iqrdata['all']['R']['0.25']).toFixed(0) + ' to ' + (iqrdata['all']['R']['0.75']).toFixed(0));

      });

  });
}

drawGraph()
