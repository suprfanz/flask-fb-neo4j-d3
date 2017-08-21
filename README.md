# SuprFanz.com Tutorial: Importing Data from Facebook into Neo4j for D3 Data Visualizaion Step by Step

The purpose of this lab is connect to the Facebook API using python and import Event data into 
[Neo4j](https://neo4j.com/) and present the data in a simple attractive graph visualization via [D3](https://d3js.org/). 

## Getting Started

To get started download/clone this project and set up a project in your favorite IDE.

### Facebook

You need an access token to make a call to the Facebook API to pull data, so you obtain one by logging into your website with Facebook. 

You will need to set up and connect your own [Facebook app](https://developers.facebook.com/docs/apps/register) in the settings in Views.py. Make sure the URL that you are using to run the application is the one in your Facebook application Settings > Basic > 
Site URL. It is not recommended that you change any other oAuth or website settings or add anymore URLs anywhere except in special cases.

If you're running the project locally, you have to use an IP address. Facebook won't let you use "localhost" but you can have a port number.

```
# Facebook app details
FB_APP_ID = '###############'
FB_APP_NAME = 'SuprFanz Data Visualization Demo'
FB_APP_SECRET = '###################################'
# Fill in ### with your own app details

```
The access token is obtained from the Facebook cookie and then stored in the session dict and the database upon login to be used in API calls later.

### Neo4j 

You can download and set up your own local instance of [Neo4j](https://neo4j.com/download/?ref=home) or run Neo4j in the [Neo4j Sandbox](https://neo4j.com/sandbox-v2/). Connect your Neo4j database in config.py
```
# Database details
neo4j_password = '########'
neo4j_admin = 'neo4j'
neo4j_dbip = '###.###.##.##'
# Fill in ### with your own db details
```

When you enter an event in the form, guest and event nodes and their relationships will be created in your database. It's best to start with a clean database dedicated to this project.

### Python 3.x and Flask

This project is based on the [Facebook SDK Flask Example](https://github.com/mobolic/facebook-sdk/tree/master/examples/flask). Install Python 3.x. Pip install requirements to a virtualenv
```
pip install -r requirements
```
To import Facebook events there is an option to use the FacebookEvents class or just the individual functions in run_get_facebook_event.py. The project is set up to use the class by default but some people prefer not to.

The class is called with:
```
    event_id = facebook_event_id
    token = facebook_token
    facebookevents = FacebookEvents(event_id, token)
    facebookevents.get_facebook_event()
    facebookevents.get_event_owner()
    facebookevents.get_rsvps()
```

If you don't use the class, change the import statement in views.py from

```
from app.facebookevent.run_get_facebook_event_class import FacebookEvents
```

to 

```
from app.facebookevent.run_get_facebook_event import get_facebook_event_main
```
then call the function with 

```
get_facebook_event_main(event_id, token)
```

Both need to be passed the Facebook event id and a valid access token.

The Facebook event ID is in the URL for a Facebook event and is a unique identifier Facebook uses for events. It is not always the same length. The JavaScript form validation ensures that this ID is what gets passed into the Python function rather than the whole URL.
```
https://www.facebook.com/events/###############/
# The ### is the event ID
```

The script neo4j2d3_mb.py converts your Neo4j data to D3 json to be used in the D3 visualization. It creates a json file in static/data. You will need to change the path to your own local or server path

    with open(
            "C:\\Users\\yourusername\\Documents\\path\\to\\neo4j2d3\\app\\static\\data\\neo4j2d3_new.json",
            "w") as f:
        f.write(graphjson)
        
This file gets overwritten every time the page is loaded when the user is logged in to ensure the latest data from the database is used. If you have a large amount of data, it might slow performance, in which case you could disable or move this function (main()) from the main view.
 
 ```
 @app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        main()
        # converts the neo4j data into graphjson
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user=g.user)

```
The required json format is basically a flat list of nodes and then a flat list of links(edges). The links must have a source and target that correspond to the nodes they're related to. See neo4j2d3_bak.json for an example of the correct json format
```
{
  "nodes": [
    {
      "name": "Person's Name",
      "id": "###############",
      "group": 1
    }
  ],
  "links": [
    {
      "value": 2,
      "target": "139767396627545",
      "source": "10155657238769380",
      "rsvp": "unsure"
    }
  ]
}
```

You can modify the [Cypher](https://neo4j.com/developer/cypher-query-language/) queries to your particular data set as long as the resulting json is in the correct format.

```
def create_guest_node():
    # fetches the guest nodes from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)
    WITH collect({id: a.fb_usr_id, name: a.fb_guest_name, group: 1}) AS nodes RETURN nodes
    '''
```

The JavaScript relies on the properties 'name', 'id' and 'group' for nodes and for links 'source', 'target', 'rsvp', and 'value' for links. If you change the property names in your database, you will have to change the corresponding properties in neo4j2d3_mb.py and the javascript in index.html to ensure the new names are mapped correctly. In this case, we are using 'group' and 'value' as arbitrary values assigned to node and link types in order to differentiate them in our visualization.


## Running

The application will create event and guest nodes and relationships using the Facebook events that you import. Therefore specific property key values are expected. Your database should be empty the first time you run it. 

1. Start Neo4J. 
2. Run the application run.py. 
3. Open your website URL in the latest Chrome on desktop (other browsers not yet supported).
4. Click the login button. There will be a Facebook popup. Login in using your Facebook account.
5. Accept the permissions the application asks for the first time (public profile)
6. Once the popup closes, the page should automatically reload, but if it doesn't, refresh.
7. Copy and paste a Facebook event URL into the form and press Import
8. You will see a visualization of the data. If you use a very large event, this could take a minute or more to load.
9. When you click on the nodes, you will see information and a Facebook picture of the person the node corresponds to.
10. You can click on the edges to see the edge type and the nodes it's related to.

### Options

We are using a simple D3 layout based on [Mike Bostock's Force-Directed graph](https://bl.ocks.org/mbostock/4062045). Display, styling, animations and other options can be set in the D3 javascript in index.html. Click and other event functions can be attached to the links and nodes. Here we have added jQuery to populate the info box with node and link properties, include Facebook pictures and profile links when clicked. In the simulation force use id to map the links to your node ids, index, or another property in your data set.

We are using the value property of links to set color, distance and strength. We have set the value to correspond to a particular RSVP type. We have two groups of nodes, events and guests, and we use the group property to assign the nodes a different color and radius.

```
 // D3 force layout
    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink()
            .distance(function (d) {
                return (3 - (d.value / 3)) * 66;
            })
            .strength(function (d) {
                return (3 - (d.value / 3)) * 0.5;
            })
            .id(function (d) {
                return d.id;
            }))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    d3.json(dataSource, function (error, graph) {
        if (error) throw error;

        var link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("stroke", function (d) {
                var colorstroke;
                //different edge colors based on edge value
                switch (d.value) {
                    case 1:
                        colorstroke = "#CCC";
                        break;
                    case 2:
                        colorstroke = "#ffa726";
                        break;
                    case 3:
                        colorstroke = "#b2ff59";
                        break;
                    default:
                        colorstroke = "#CCC";
                }
                return colorstroke;
            });

        var node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("r", function (d) {
                return (d.group === 0 ? 15 : 5);
            })
            .attr("fill", function (d) {
                return (d.group === 0 ? '#fdd835' : '#90caf9');
            })
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged));
//              .on("end", dragended));

        //show the node's name property on hover
        node.append("title")
            .text(function (d) {
                return d.name;
            });

        //add click function to nodes
        node.on("click", showinfo);

        //show the link's rsvp property on hover
        link.append("title")
            .text(function (d) {
                return d.rsvp;
            });

        //add click function to links
        link.on("click", showinfo);

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(graph.links);

        function ticked() {
            link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node
                .attr("cx", function (d) {
                    return d.x;
                })
                .attr("cy", function (d) {
                    return d.y;
                });
        }
    });

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }
```
For more options, see [D3](https://d3js.org/) docs and examples


## Notes
This app does not yet contain a test to check if the Facebook event is valid, only that the URL passes the regex. This does not take into account when a user added an event and then later cancelled it or when the URL otherwise passes the regex but still does not match an existing event. There still needs to be an API request that throws an exception when the request is a 404 in the validation process. This is planned for a future release.

Private events are not currently supported as this require extending the app permissions which would call for a [Facebook review](https://developers.facebook.com/docs/facebook-login/overview). The assumption is that only the default public profile permissions are requested. A developer could change this in the [permissions scope](https://developers.facebook.com/docs/facebook-login/permissions/requesting-and-revoking) requested to allow for their own private events data to be pulled and no review would be required if the app was in developer test mode.

In the Facebook Graph API the edge "unsure" is used to describe people who have responded to an event as either "Maybe" or "Interested".


## Built With

* [Neo4j](https://neo4j.com/) - Non-relational Graph database
* [Python](https://www.python.org/) - programming language.
* [Flask](https://rometools.github.io/rome/) - a microframework for Python
* [D3](https://d3js.org/) - A graph visualization api

## Contributing

We welcome contributions to this project and are open to ideas. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Ray Bernard** - [@SuprFanz](https://github.com/suprfanz)
* **Jen Webb** - [@jndoy](https://github.com/jndoy)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Facebook-SDK](https://github.com/mobolic/facebook-sdk/tree/master/examples/flask)
* [Mike Bostock](https://bl.ocks.org/mbostock/4062045)

