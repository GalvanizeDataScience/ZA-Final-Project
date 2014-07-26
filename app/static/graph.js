var width = 960, height = 500;

var color = d3.scale.category20();

var svg = d3.select("div.graph").append("svg")
    .attr("width", width)
    .attr("height", height);

var force = d3.layout.force()
    .nodes(graph.nodes)
    .links(graph.links)
    .size([width, height])
    .linkDistance(30)
    .charge(-120)
    .on("tick", tick)
    .start();

var link = svg.selectAll(".link")
    .data(graph.links)
    .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", function(d) { return Math.sqrt(d.value); });

var node = svg.selectAll(".node")
    .data(graph.nodes)
    .enter().append("circle")
        .attr("class", "node")
        .attr("name", function(d) { return d.name; })
        .attr("r", function(d) { return d.comm_size * 2; })
        .style("fill", function(d) { return color(d.group); })
        .call(force.drag);

node.append("text")
    .attr("x", 12)
    .attr("dy", ".35em")
    .text(function(d) { return d.name; });

function tick() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
}


$(document).ready(function(){

    var obj = graph.root

    $("span.id").text(obj['id_'])
    $("span.name").text(obj['name_'])
    $("span.description").text(obj['description'])
    $("span.followers_count").text(obj['followers_count'])
    $("span.friends_count").text(obj['friends_count'])
});


$(document).ready(function(){
    $("circle.node").click(function(){

        var obj = $(this)[0]['__data__']

        $("span.comm_size").text(obj['comm_size'])
        $("span.density").text(obj["density"])
        $("span.group").text(obj["group"])
        $("span.hashtags").text(obj["hashtags"])
        $("span.mentioned").text(obj["mentioned"])
        $("span.modularity").text(obj["modularity"])
        $("span.most_connected").text(obj["most_connected"])

        if(obj["sentiment"][0] > 6.5) {
            $("span.sentiment").text("Happy")
        } else if(obj["sentiment"][0] < 4.5) {
            $("span.sentiment").text("Sad")
        } else {
            $("span.sentiment").text("Neutral")
        }

        $("span.topics").text('')
        $.each(obj["topics"], function(k0,v0) {
            var topics = []
            $.each(v0, function(k1, v1) {
                topics.push(v1[0])
            })
            $("span.topics").append(topics.join() + '<br>')
        })

    });
});
