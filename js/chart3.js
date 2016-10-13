// Set the dimensions of the canvas / graph
var chart3margin = {top: 30, right: 20, bottom: 30, left: 70},
    chart3width = parseInt(d3.select('#chart2').style('width')) - chart3margin.left - chart3margin.right,
    chart3height = 820 - chart3margin.top - chart3margin.bottom;

var circle_rad = 4
var animation_time = 1000

// Set the ranges
var chart3x = d3.scale.linear().rangeRound([0, chart3width]);
var chart3y = d3.scale.ordinal().rangeRoundBands([chart3height, 0], 0);

// Define the axes
var chart3xAxis = d3.svg.axis()
    .scale(chart3x)
    .orient("top")
    .tickFormat(d3.format('.0%'));

var chart3yAxis = d3.svg.axis()
    .scale(chart3y)
    .orient("left");

// Adds the svg canvas
var chart3 = d3.select("div#chart3").append("svg")
    .attr("width", chart3width + chart3margin.left + chart3margin.right)
    .attr("height", chart3height + chart3margin.top + chart3margin.bottom)
  .append("g")
    .attr("transform", "translate(" + chart3margin.left + "," + chart3margin.top + ")");

var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("display", "none");

// Get the data
d3.csv("output/surplus_by_state.csv", function(error, data) {

  data.sort(function(a, b) {return a['Average'] - b['Average'];});
  // Scale the range of the data
  chart3y.domain(data.map(function(d) { return (d.State); }));
  chart3x.domain([-.55, .55]);

  chart3.append("g")
      .attr("class", "x axis")
      .call(chart3xAxis);

  chart3.append("g")
      .attr("class", "y axis")
      .call(chart3yAxis);

  chart3.selectAll('.staterect')
      .data(data)
    .enter().append('rect')
      .attr('class','staterect')
      .attr('id',function(d) {return d.State;})
      .attr('x', 1)
      .attr('y', function(d) { return chart3y(d.State); })
      .attr('height', function(d) { return chart3y.rangeBand();})
      .attr('width', chart3width-1)
      .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            d3.select('#'+d.State)
                .style('fill','#303636');
            div	.html(d.State_Full + ",<span style='font-weight:bold'> " + d.Total_Reps + "</span> Reps" + "<br/><span style='font-weight:bold'>" + Math.abs(d.Average*100).toFixed(1) + '%</span> Misrepresented' + '<br/><span style="font-weight:bold">' + (d.Mis_Reps*1).toFixed(2) + '</span> Reps Gerrymandered')
                .style('display', 'inline')
                .style("left", (d3.event.pageX - 70) + "px")
                .style("top", (d3.event.pageY - 60) + "px");

            })
      .on('mousemove', function(d) {
          div
              .style("left", (d3.event.pageX - 70) + "px")
              .style("top", (d3.event.pageY - 60) + "px");
      })
      .on("mouseout", function(d) {
          div.transition()
              .duration(200)
              .style("opacity", 0);
          d3.select('#'+d.State)
              .style('fill','#191c1c');
      });

  chart3.append('line')
      .attr('x1', chart3width/2)
      .attr('x2', chart3width/2)
      .attr('y1', 1)
      .attr('y2', chart3height - chart3y.rangeBand()/2 - 1)
      .style('stroke','#919191')
      .style('stroke-dasharray','5,5')
      .style('stroke-width',1);

  chart3.selectAll('.stateline')
      .data(data)
    .enter().append('line')
      .attr('class','stateline')
      .style('stroke','#919191')
      .style('stroke-dasharray','2,4')
      .style('stroke-width',1)
      .attr('x1', 1)
      .attr('x2', chart3width)
      .attr('y1', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));})
      .attr('y2', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));});

  chart3.selectAll('.avgline')
      .data(data)
    .enter().append('line')
      .attr('id', function(d) { return (d.Average==0 ? 'zero' : 'non-zero'); })
      .attr("class", function(d) { return "avgline " + (d.Average < 0 ? "negative" : "positive"); })
      .style('stroke-width',3)
      .attr('x1', function(d) { return chart3x(d.Average);})
      .attr('x2', function(d) { return chart3x(d.Average);})
      .attr('y1', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand())-1);})
      .attr('y2', function(d) { return (chart3y((d.State))+1);});

  var years = ['y2004','y2006','y2008','y2010','y2012','y2014']
  for (var i = 0; i < years.length; i++) {
  chart3.selectAll('.dot' + years[i].substring(3,5))
      .data(data)
    .enter().append('circle')
      .attr('class','dot' + years[i].substring(3,5))
      .attr('r', circle_rad)
      .style('opacity',0.2)
      .attr('cx', function(d) { return chart3x(d[years[i]]);})
      .attr('cy', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));});
  }

});

var sortMisreps = function() {
  d3.csv("output/surplus_by_state.csv", function(error, data) {

    data.sort(function(a, b) {return a['Mis_Reps'] - b['Mis_Reps'];});

    chart3y.domain(data.map(function(d) { return (d.State); }));

    chart3.selectAll('g.y.axis text')
        .transition().duration(animation_time/2)
        .style('opacity',0)
        .remove();

    chart3.append("g")
        .attr("class", "y axis")
        .attr('id','Misreps')
        .style('opacity',0)
        .call(chart3yAxis);

    chart3.selectAll('g#Misreps.y.axis')
        .transition().delay(250).duration(animation_time/2)
        .style('opacity',1);

    chart3.selectAll('.staterect')
        .attr('y', function(d) { return chart3y(d.State); })
        .on("mouseover", function(d) {
              div.transition()
                  .duration(200)
                  .style("opacity", .9);
              div	.html(d.State_Full + ",<span style='font-weight:bold'> " + d.Total_Reps + "</span> Reps" + "<br/><span style='font-weight:bold'>" + Math.abs(d.Average*100).toFixed(1) + '%</span> Misrepresented' + '<br/><span style="font-weight:bold">' + (d.Mis_Reps*1).toFixed(2) + '</span> Reps Gerrymandered')
                  .style("left", (d3.event.pageX - 70) + "px")
                  .style("top", (d3.event.pageY - 60) + "px")
                  .style('display', 'inline');
              d3.select('#'+d.State)
                  .style('fill','#303636');
              })
        .on('mousemove', function(d) {
            div
                .style("left", (d3.event.pageX - 70) + "px")
                .style("top", (d3.event.pageY - 60) + "px");
        })
        .on("mouseout", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", 0);
            d3.select('#'+d.State)
                .style('fill','#191c1c');
        });

    chart3.selectAll('.avgline')
        .transition().duration(animation_time)
        .attr('y1', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand())-1);})
        .attr('y2', function(d) { return (chart3y((d.State))+1);});

    var years = ['y2004','y2006','y2008','y2010','y2012','y2014']
    for (var i = 0; i < years.length; i++) {
    chart3.selectAll('.dot' + years[i].substring(3,5))
        .transition().duration(animation_time)
        .attr('cy', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));});
    }

  });
}

var sortAverage = function() {
  d3.csv("output/surplus_by_state.csv", function(error, data) {

    data.sort(function(a, b) {return a['Average'] - b['Average'];});

    chart3y.domain(data.map(function(d) { return (d.State); }));

    chart3.selectAll('g.y.axis text')
        .transition().duration(animation_time/2)
        .style('opacity',0)
        .remove();

    chart3.append("g")
        .attr("class", "y axis")
        .attr('id','Average')
        .style('opacity',0)
        .call(chart3yAxis);

    chart3.selectAll('g#Average.y.axis')
        .transition().delay(250).duration(animation_time/2)
        .style('opacity',1);

    chart3.selectAll('.staterect')
        .attr('y', function(d) { return chart3y(d.State); })
        .on("mouseover", function(d) {
              div.transition()
                  .duration(200)
                  .style("opacity", .9);
              div	.html(d.State_Full + ",<span style='font-weight:bold'> " + d.Total_Reps + "</span> Reps" + "<br/><span style='font-weight:bold'>" + Math.abs(d.Average*100).toFixed(1) + '%</span> Misrepresented' + '<br/><span style="font-weight:bold">' + (d.Mis_Reps*1).toFixed(2) + '</span> Reps Gerrymandered')
                  .style("left", (d3.event.pageX - 70) + "px")
                  .style("top", (d3.event.pageY - 60) + "px")
                  .style('display', 'inline');
              d3.select('#'+d.State)
                  .style('fill','#303636');
              })
        .on('mousemove', function(d) {
            div
                .style("left", (d3.event.pageX - 70) + "px")
                .style("top", (d3.event.pageY - 60) + "px");
        })
        .on("mouseout", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", 0);
            d3.select('#'+d.State)
                .style('fill','#191c1c');
        });

    chart3.selectAll('.avgline')
        .transition().duration(animation_time)
        .attr('y1', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand())-1);})
        .attr('y2', function(d) { return (chart3y((d.State))+1);});

    var years = ['y2004','y2006','y2008','y2010','y2012','y2014']
    for (var i = 0; i < years.length; i++) {
    chart3.selectAll('.dot' + years[i].substring(3,5))
        .transition().duration(animation_time)
        .attr('cy', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));});
    }

  });
}

var sortReps = function() {
  d3.csv("output/surplus_by_state.csv", function(error, data) {

    data.sort(function(a, b) {return a['Total_Reps'] - b['Total_Reps'];});

    chart3y.domain(data.map(function(d) { return (d.State); }));

    chart3.selectAll('g.y.axis text')
        .transition().duration(animation_time/2)
        .style('opacity',0)
        .remove();

    chart3.append("g")
        .attr("class", "y axis")
        .attr('id','Reps')
        .style('opacity',0)
        .call(chart3yAxis);

    chart3.selectAll('g#Reps.y.axis')
        .transition().delay(animation_time/2).duration(animation_time/2)
        .style('opacity',1);

    chart3.selectAll('.staterect')
        .attr('y', function(d) { return chart3y(d.State); })
        .on("mouseover", function(d) {
              div.transition()
                  .duration(200)
                  .style("opacity", .9);
              div	.html(d.State_Full + ",<span style='font-weight:bold'> " + d.Total_Reps + "</span> Reps" + "<br/><span style='font-weight:bold'>" + Math.abs(d.Average*100).toFixed(1) + '%</span> Misrepresented' + '<br/><span style="font-weight:bold">' + (d.Mis_Reps*1).toFixed(2) + '</span> Reps Gerrymandered')
                  .style("left", (d3.event.pageX - 70) + "px")
                  .style("top", (d3.event.pageY - 60) + "px")
                  .style('display', 'inline');
              d3.select('#'+d.State)
                  .style('fill','#303636');
              })
        .on('mousemove', function(d) {
            div
                .style("left", (d3.event.pageX - 70) + "px")
                .style("top", (d3.event.pageY - 60) + "px");
        })
        .on("mouseout", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", 0);
            d3.select('#'+d.State)
                .style('fill','#191c1c');
        });

    chart3.selectAll('.avgline')
        .transition().duration(animation_time)
        .attr('y1', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand())-1);})
        .attr('y2', function(d) { return (chart3y((d.State))+1);});

    var years = ['y2004','y2006','y2008','y2010','y2012','y2014']
    for (var i = 0; i < years.length; i++) {
    chart3.selectAll('.dot' + years[i].substring(3,5))
        .transition().duration(animation_time)
        .attr('cy', function(d) { return (chart3y((d.State)) + (chart3y.rangeBand()/2));});
    }

  });
}


function type(d) {
  d.y2004 = +d.y2004;
  d.y2006 = +d.y2006;
  d.y2008 = +d.y2008;
  d.y2010 = +d.y2010;
  d.y2012 = +d.y2012;
  d.y2014 = +d.y2014;
  d.Average = +d.Average;
  d.Total_Reps = +d.Total_Reps;
  return d;
}
