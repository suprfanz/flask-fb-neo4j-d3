# SuprFanz.coTutorial: Importing Data from Facebook into Neo4j for D3 Data Visualizaion Step by Step

## UPDATE
As of April 4, 2018, Facebook has changed the Graph API so event guest edges can no longer be accessed (the RSVP list). Read more [here](https://newsroom.fb.com/news/2018/04/restricting-data-access/) and [here](https://developers.facebook.com/blog/post/2018/04/04/facebook-api-platform-product-changes/). This app can be repurposed to pull other edges from the Graph API that are still currently allowed into Neo4j in order to visualize them in D3, however it will have to be refactored. We are working on this and will provide an update soon.
- Jen Webb

The purpose of this lab is connect to the [Facebook API](https://developers.facebook.com/docs/graph-api) using Flask python,  import Event data into 
[Neo4j](https://neo4j.com/) and present it in a simple attractive graph visualization via [D3](https://d3js.org/). 

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
FB_APP_NAME = 'Your App Name'
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
Models.py  is where the User class is, which is how the user gets registered and logged in. When connecting to the app by Facebook for the first time, the user logs into Facebook and says yes to give the app permissions. Then the script looks to see if the user already exists in the database, and if they don't, a new User node is created in the database. 

```
def create_user(self):
# creates the user
insert_query = '''
MERGE (n:user{id:{id}, name:{name},profile_url:{profile_url}, access_token:{access_token}})

'''
with  GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                           auth=basic_auth("neo4j", "{}".format(neo4j_password))) as driver:
    with driver.session() as session:
        session.run(insert_query, parameters={"id": self.id,
                                              "name": self.name,
                                              "profile_url": self.profile_url,
                                              "access_token": self.access_token
                                              })
```
 
 The next time the user logs in

To import Facebook events there is the FacebookEvents class.

The class is called with:
```
    event_id = facebook_event_id
    token = facebook_token
    facebookevents = FacebookEvents(event_id, token)
    facebookevents.get_facebook_event()
    facebookevents.get_event_owner()
    facebookevents.get_rsvps()
```

It needs to be passed the Facebook event id and a valid access token.

The Facebook event ID is in the URL for a Facebook event and is a unique identifier Facebook uses for events. It is not always the same length. The JavaScript form validation ensures that this ID is what gets passed into the Python function rather than the whole URL.
```
https://www.facebook.com/events/###############/
# The ### is the event ID
```

The script neo4j2d3_mb.py converts your Neo4j data to D3 JSON to be used in the D3 visualization. It creates a JSON file in static/data. You will need to change the path to your own local or server path

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
The JSON format is basically a flat list of nodes and then a flat list of links(edges). The links must have a source and target that correspond to the nodes they're related to. See neo4j2d3_bak.json for an example of the correct JSON format
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

You can modify the [Cypher](https://neo4j.com/developer/cypher-query-language/) queries to your particular data set as long as the resulting JSON is in the correct format.

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

1. Start Neo4J locally or make sure it's running online. 
2. Run the application file run.py. 
3. Open your website URL in the latest Chrome on desktop (other browsers not yet supported). If you're running this locally, it has to be accessed with your IP address not localhost.
4. Click the login button. There will be a Facebook popup. Login in using your Facebook account.
5. Accept the permissions the application asks for the first time (public profile)
6. Once the popup closes, the page should automatically reload, but if it doesn't, refresh.
7. Copy and paste a Facebook event URL into the form and press Import
8. You will see a visualization of the data. If you use a very large event, this could take a minute or more to load.
9. When you click on the nodes, you will see information and a Facebook picture of the person the node corresponds to.
10. You can click on the edges to see the edge type and the nodes it's related to.

### Options

We are using a simple D3 layout based on [Mike Bostock's Force-Directed graph](https://bl.ocks.org/mbostock/4062045). Display, styling, animations and other options can be set in the D3 javascript in index.html. Click and other event functions can be attached to the links and nodes. 

We are using the value property of links to set color, distance and strength. We have set the value to correspond to a particular RSVP type. We have two groups of nodes, events and guests, and we use the group property to assign the nodes a different color and radius. We also made the graph fit any size screen on load and added the zoom functionality:

```
var focus_node = null,
    highlight_node = null,
    highlight_color = "#d32f2f",
    highlight_trans = 0.1,
    outline = false,
    timeStamp = Math.floor(Date.now() / 1000),
    dataSource = "/static/data/neo4j2d3_new.json" + "?time=" + timeStamp,
    width = $('body').width(),
    height = $('body').height(),
    svg = d3.select("svg")
    .attr("width", width)
    .attr("height", height)
    .call(d3.zoom().on("zoom", function () {
       svg.selectAll('g').attr("transform", d3.event.transform)
    }));

// D3 force layout
```

Here we have added jQuery to populate the info box with node and link properties, include Facebook pictures and profile links when clicked. In the simulation force use id to map the links to your node ids, index, or another property in your data set.

```
 function showinfo(d) {
    //display info about nodes and edges in info box when clicked
    var nameTxt = $('#name'),
        propTxt = $('#properties'),
        typeTxt = $('#type'),
        fbPic = $('#fb_pic');
    //remove selected class from all other elements
    $('.nodes circle, .links line').not(this).removeClass("selected");

    if (!$(this).is('.selected')) {
        //if the clicked element doesn't have the selected class, add it
        this.setAttribute('class', "selected");

        if (d.id) {
            console.log('node');
            nameTxt.html('<b>Node:</b> <a href="https://www.facebook.com/' + d.id + '" target="_blank">' + d.name + '</a>');
            propTxt.html('<b>ID</b>: ' + d.id);
            typeTxt.html('<b>Type</b>: ' + (d.group === 0 ? 'Event' : 'Guest'));
            fbPic.css({'background-image': 'url("https://graph.facebook.com/' + d.id + '/picture?type=large&width")'});
        } else {
            console.log('edge');
            nameTxt.html('<b>Edge</b>: ' + d.rsvp);
            propTxt.html('<b>Source:</b> ' + (d.source.group === 0 ? 'Event - ' : 'Guest - ') + ' ' + d.source.name);
            typeTxt.html('<b>Target:</b> ' + (d.target.group === 0 ? 'Event - ' : 'Guest - ') + ' ' + d.target.name);
            fbPic.css({'background-image': ''});
        }

        console.log(d);

    } else {
        //if the clicked element has the selected class remove it
        $(this).removeClass('selected');
        //remove the information about the previous selected element
        nameTxt.html('');
        propTxt.html('');
        typeTxt.html('');
        fbPic.css({'background-image': ''});
    }
}
```
For more options, see [D3](https://d3js.org/) docs and examples.


## Notes
This app does not yet contain a test to check if the Facebook event is valid, only that the URL passes the regex. This does not take into account when a user added an event and then later cancelled it or when the URL otherwise passes the regex but still does not match an existing event. There still needs to be an API request that throws an exception when the request is a 404 in the validation process. This is planned for a future release.

Private events are not currently supported as this require extending the app permissions which would call for a [Facebook review](https://developers.facebook.com/docs/facebook-login/overview). The assumption is that only the default public profile permissions are requested. A developer could change this in the [permissions scope](https://developers.facebook.com/docs/facebook-login/permissions/requesting-and-revoking) requested to allow for their own private events data to be pulled and no review would be required if the app was in developer test mode.

The event data does not continuously update in real time, but you can update an event by importing it again with the form.

In the Facebook Graph API the edge "unsure" is used to describe people who have responded to an event as either "Maybe" or "Interested".

Browsers other than the latest Chrome on Windows have not been tested.

## Built With

* [Neo4j](https://neo4j.com/) - Non-relational Graph database
* [Python](https://www.python.org/) (version 3.4.3) - programming language.
* [Flask](https://rometools.github.io/rome/) - a microframework for Python
* [D3](https://d3js.org/) (version 4.0) - A graph visualization api

## Contributing

We welcome contributions to this project and are open to ideas. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors / Collaborators

* **Ray Bernard** - [@SuprFanz](https://github.com/suprfanz)
* **Jen Webb** - [@jenwebb](https://github.com/jenwebb)
* **Alexei Demchouk** - [@aleksod](https://github.com/aleksod)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Facebook-SDK](https://github.com/mobolic/facebook-sdk/tree/master/examples/flask)
* [Mike Bostock](https://bl.ocks.org/mbostock/4062045)
* We use the [Neo4j bolt driver for Python](https://github.com/neo4j/neo4j-python-driver) exclusively to connect to Neo4j but if you want to see an example of a Flask application that uses [Py2Neo](https://github.com/technige/py2neo), check out Nicole White's [neo4j-flask](https://github.com/nicolewhite/neo4j-flask).
