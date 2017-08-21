from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for, jsonify
from app import app
from app.models import User
from app.facebookevent.run_get_facebook_event_class import FacebookEvents
from neo4j2d3_mb import main

# Add your Facebook app details
FB_APP_ID = '###############'
FB_APP_NAME = 'Your Facebook App Name'
FB_APP_SECRET = '################################'


@app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        main()
        # converts the neo4j data into graphjson
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user=g.user)
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/import-event', methods=['POST'])
def importevent():
    # takes event entered in form and imports into neo4j
    if g.user:
        # this needs to be a valid Facebook event id. The javascript converts it from the URL
        event_id = request.form['event_url']
        access_token = session.get('user')['access_token']
        facebookevents = FacebookEvents(event_id, access_token)
        facebookevents.get_facebook_event()
        facebookevents.get_rsvps()
        # pulls event data from facebook and imports it into neo4j
        main()
        # converts the neo4j data into graphjson
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Log out the user from the application.

    Log out the user from the application by removing them from the
    session.  Note: this does not log the user out of Facebook - this is done
    by the JavaScript SDK.
    """
    session.pop('user', None)
    return redirect(url_for('index'))


@app.before_request
def get_current_user():
    """Set g.user to the currently logged in user.

    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.

    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get('user'):
        g.user = session.get('user')
        return

    # Attempt to get the short term access token for the current user.
    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                  app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        graph = GraphAPI(result['access_token'])

        profile = graph.get_object('me')

        if 'link' not in profile:
            # Check to see if this user is already in our database.
            profile['link'] = ""
            user = User(result['uid'], name=profile['name'], profile_url=profile['link'],
                        access_token=result['access_token'])

            user = user.check_user()

            if not user:
                # Not an existing user so get info
                graph = GraphAPI(result['access_token'])
                profile = graph.get_object('me')
                if 'link' not in profile:
                    profile['link'] = ""

                    # Create the user and insert it into the database '

                    user = User(result['uid'], profile['name'], profile['link'], result['access_token'])
                    user.create_user()

            elif user['access_token'] != result['access_token']:
                # If an existing user, update the access token
                user['access_token'] = result['access_token']

            # Add the user to the current session
            session['user'] = dict(name=profile['name'], profile_url=profile['link'],
                                   id=result['uid'], access_token=result['access_token'])

    # Commit changes to the database and set the user as a global g.user
    g.user = session.get('user', None)
