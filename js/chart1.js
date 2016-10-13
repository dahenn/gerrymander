// Set the dimensions of the canvas / graph
var margin = {top: 10, right: 20, bottom: 30, left: 50},
    width = parseInt(d3.select('#chart1').style('width')) - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

// Set the ranges
var x = d3.scale.linear().rangeRound([0, width]);
var y = d3.scale.ordinal().rangeRoundBands([height, 0], .15);
var color = d3.scale.ordinal()
    .range(["#4b50af", "#a03030"]);

// Define the axes
var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickFormat(d3.format('.0%'));

var yAxis = d3.svg.axis()
    .scale(y)
    .outerTickSize(0)
    .orient("left");

// Adds the svg canvas
var svg = d3.select("div#chart1").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Get the data
d3.csv("output/vote_share_by_year.csv", function(error, data) {
  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "year"; }));

  data.forEach(function(d) {
    var y0 = 0;
    d.seats = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
    d.total = d.seats[d.seats.length - 1].y1;
  });

  // Scale the range of the data
  y.domain(data.map(function(d) { return d.year; }));
  x.domain([0, 1]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  var shares = svg.selectAll(".votes")
      .data(data)
    .enter().append("g")
      .attr("class", "votes")
      .attr("transform", function(d) { return "translate(0," + y(d.year) + ")"; });

  shares.selectAll("rect")
      .data(function(d) { return d.seats; })
    .enter().append("rect")
      .attr("height", y.rangeBand())
      .attr("x", function(d) { return x(d.y0); })
      .attr("width", function(d) { return x(d.y1) - x(d.y0); })
      .attr('class', function(d) { return d.name; })
      .style("fill", function(d) { return color(d.name); });

  shares.selectAll("rect.diff")
      .data(function(d) { return d.seats; })
    .enter().append("rect")
      .attr("height", y.rangeBand())
      .attr("x", function(d) { return x(d.y0); })
      .attr("width", 0)
      .attr("class", function(d) { return "diff " + d.name; })
      .style("fill", function(d) { return color(d.name); });

  shares.selectAll('text')
      .data(function(d) { return d.seats; })
    .enter().append("text")
      .attr('y', y.rangeBand()/2)
      .attr('dy','0.5em')
      .attr("x", function(d, i) { return x(d.y1) + (x(d.y0) - x(d.y1))/2; })
      .style('text-anchor', 'middle')
      .attr('class','label')
      .text(function(d) { return ((d.y1 - d.y0)*100).toFixed(0) + "%"; });

});

// ** Update data section (Called from the onclick)
function updateData() {
    //d3.selectAll('rect').transition().duration(650).remove();

    // Get the data again
    d3.csv("output/seat_shares_by_year.csv", function(error, data) {
      data.forEach(function(d) {
        var y0 = 0;
        d.seats = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
        d.total = d.seats[d.seats.length - 1].y1;
        d.diff = +d.diff;
      });

    // Select the section we want to apply our changes to
    var shares = svg.selectAll(".votes").data(data);
    var r_shares = svg.selectAll('.share_R.diff').data(data);

    rects = shares.selectAll("rect");
    labels = shares.selectAll('text');

    /*rects.data(function(d) { return d.seats; })
        .transition().duration(650).ease('linear')
        .attr("x", function(d) { return x(d.y0); })
        .attr("width", function(d) { return x(d.y1) - x(d.y0); });*/

    r_shares.data(data)
        .style('fill', function(d) { return (d.diff < 0 ? "#8e1111" : "#2a30a8"); })
        .transition().duration(650).ease('linear')
        .attr('x', function(d) { return (d.diff < 0 ? x(d.share_D) + 1 : x(d.share_D) - x(d.diff)); })
        .attr("width", function(d) { return x(Math.abs(d.diff)); });


    labels.data(function(d) { return d.seats; })
        .transition().duration(650).ease('linear')
        .attr("x", function(d, i) { return x(d.y1) + (x(d.y0) - x(d.y1))/2; })
        .text(function(d) { return ((d.y1 - d.y0)*100).toFixed(0) + "%"; });

    });

}

// ** Update data section (Called from the onclick)
function revertData() {
  //d3.selectAll('rect').remove();
  // Get the data again
  d3.csv("output/vote_share_by_year.csv", function(error, data) {
    data.forEach(function(d) {
      var y0 = 0;
      d.seats = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
      d.total = d.seats[d.seats.length - 1].y1;
    });

  // Select the section we want to apply our changes to
  var shares = svg.selectAll(".votes").data(data);
  var r_shares = svg.selectAll('.share_R.diff').data(data);

  rects = shares.selectAll("rect");
  labels = shares.selectAll('text');

  r_shares.data(data)
      .transition().duration(650).ease('linear')
      .attr("x", function(d) { return x(d.share_D); })
      .attr("width", 0);

  labels.data(function(d) { return d.seats; })
      .transition().duration(650).ease('linear')
      .attr("x", function(d, i) { return x(d.y1) + (x(d.y0) - x(d.y1))/2; })
      .text(function(d) { return ((d.y1 - d.y0)*100).toFixed(0) + "%"; });

  });
}
