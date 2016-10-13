// Set the dimensions of the canvas / graph
var chart2margin = {top: 30, right: 20, bottom: 30, left: 50},
    chart2width = parseInt(d3.select('#chart2').style('width')) - margin.left - margin.right,
    chart2height = 600 - margin.top - margin.bottom;

// Set the ranges
var chart2x = d3.scale.ordinal().rangeRoundBands([0, chart2width],0.15);
var chart2y = d3.scale.linear().range([chart2height, 0]);

// Define the axes
var chart2xAxis = d3.svg.axis().scale(chart2x)
    .orient("top");

var chart2yAxis = d3.svg.axis().scale(chart2y)
    .orient("left").ticks(9)
    .tickFormat(Math.abs);

// Adds the svg canvas
var chart2 = d3.select("div#chart2")
    .append("svg")
        .attr("width", chart2width + chart2margin.left + chart2margin.right)
        .attr("height", chart2height + chart2margin.top + chart2margin.bottom)
    .append("g")
        .attr("transform",
              "translate(" + chart2margin.left + "," + chart2margin.top + ")");

// Get the data
d3.csv("output/seat_differential.csv", function(error, data) {

    // Scale the range of the data
    chart2x.domain(data.map(function(d) { return d.index; }));
    chart2y.domain([-20,20]);

    chart2.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", function(d) { return "bar bar-" + (d.diff < 0 ? "negative" : "positive"); })
        .attr("x", function(d) { return chart2x(d.index); })
        .attr("width", chart2x.rangeBand())
        .attr("y", function(d) { return chart2y(Math.max(0,d.diff)); })
        .attr("height", function(d) { return Math.abs(chart2y(d.diff) - chart2y(0)); });

    chart2.selectAll('text')
        .data(data)
      .enter().append("text")
        .attr('x', function(d) { return chart2x(d.index) + (chart2x.rangeBand()/2); })
        .attr("y", function(d) { return chart2y(d.diff) - (chart2y(d.diff) - chart2y(0))/Math.abs((chart2y(d.diff) - chart2y(0)))*20; })
        .attr('dy', '0.5em')
        .style('text-anchor', 'middle')
        .attr('class','label')
        .text(function(d) { return Math.abs(d.diff*1).toFixed(0) });

    // Add the X Axis
    chart2.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + chart2height/2 + ")")
        .call(chart2xAxis);

    // Add the Y Axis
    chart2.append("g")
        .attr("class", "y axis")
        .call(chart2yAxis)
      .append('text')
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Democrat");

    chart2.select('g.y').append('text')
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .attr('dx', -chart2height)
        .style("text-anchor", "start")
        .text("Republican");

    chart2.select('g.y').append('text')
        .attr("transform", "rotate(-90)")
        .attr("y", -35)
        .attr('dx', -(chart2height/2))
        .style("text-anchor", "middle")
        .style('font-weight', 'bold')
        .text("Excess Seats Not Attributable to National Vote Share");

});

function type(d) {
  d.diff = +d.diff;
  return d;
}
