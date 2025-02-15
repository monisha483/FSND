#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genre = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='venue',
                            lazy=True, cascade='all, delete')

    def getVenueString(self):
      return {'id': self.id, 'name': self.name, 'genres': self.genre.split(','), 'address': self.address, 'city': self.city, 'state': self.state, 'phone': self.phone, 'website_link': self.website, 'facebook_link': self.facebook_link, 'seeking_talent': self.seeking_talent, 'seeking_description': self.seeking_description, 'image_link': self.image_link}

    def makeVenueStringWithShowCount(self):

        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state, 'phone': self.phone, 'address': self.address, 'image_link': self.image_link, 'facebook_link': self.facebook_link, 'website': self.website, 'seeking_talent': self.seeking_talent, 'seeking_description': self.seeking_description, 'num_shows': self.getUpcomingShowCount()}

    def makeVenueStringForSearch(self):
        return {'id': self.id, 'name': self.name, 'num_upcoming_shows': self.getUpcomingShowCount()}

    def makeVenueStringForShowVenue(self):

        return {'id': self.id, 'name': self.name, 'genre': self.genre.split(','), 'address': self.address, 'city': self.city, 'state': self.state, 'phone': self.phone, 'website': self.website, 'facebook_link': self.facebook_link, 'seeking_talent': self.seeking_talent, 'seeking_description': self.seeking_description, 'image_link': self.image_link, 'past_shows': self.getPastShows(), 'upcoming_shows': self.getUpcomingShows(), 'past_shows_count': self.getPastShowCount(), 'upcoming_shows_count': self.getUpcomingShowCount()}

    def getPastShows(self):
        showList = Shows.query.filter(
            self.id == Shows.venue_id, Shows.start_time < datetime.date.today()).all()
        past_shows = []
        for s in showList:
            artistObj = Artist.query.filter(s.artist_id == Artist.id).all()
            past_shows.append({'artist_id': artistObj[0].id, 'artist_name': artistObj[0].name, 'artist_image_link': artistObj[0].image_link, 'start_time': (
                s.start_time).strftime("%Y-%m-%d, %H:%M:%S")})
        return past_shows

    def getPastShowCount(self):
        return Shows.query.filter(self.id == Shows.venue_id, Shows.start_time < datetime.date.today()).count()

    def getUpcomingShows(self):
        showList = Shows.query.filter(
            self.id == Shows.venue_id, Shows.start_time > datetime.date.today()).all()
        up_shows = []
        for s in showList:
            artistObj = Artist.query.filter(s.artist_id == Artist.id).all()
            up_shows.append({'artist_id': artistObj[0].id, 'artist_name': artistObj[0].name, 'artist_image_link': artistObj[0].image_link, 'start_time': (
                s.start_time).strftime("%Y-%m-%d, %H:%M:%S")})
        return up_shows

    def getUpcomingShowCount(self):
        return Shows.query.filter(self.id == Shows.venue_id, Shows.start_time > datetime.date.today()).count()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Shows', backref='artist',
                            lazy=True, cascade='all, delete')

    def makeArtistStringForSearch(self):
        return {'id': self.id, 'name': self.name, 'num_upcoming_shows': self.getArtistUpcomingShowCount()}

    def getArtistPastShows(self):
        showList = Shows.query.filter(
            self.id == Shows.artist_id, Shows.start_time < datetime.date.today()).all()
        past_shows = []
        for s in showList:
            venueObj = Venue.query.filter(s.venue_id == Venue.id).all()
            past_shows.append({'venue_id': venueObj[0].id, 'venue_name': venueObj[0].name, 'venue_image_link': venueObj[0].image_link, 'start_time': (
                s.start_time).strftime("%Y-%m-%d, %H:%M:%S")})
        return past_shows

    def getArtistUpcomingShows(self):
        showList = Shows.query.filter(
            self.id == Shows.artist_id, Shows.start_time < datetime.date.today()).all()
        up_shows = []
        for s in showList:
            venueObj = Venue.query.filter(s.venue_id == Venue.id).all()
            up_shows.append({'venue_id': venueObj[0].id, 'venue_name': venueObj[0].name, 'venue_image_link': venueObj[0].image_link, 'start_time': (
                s.start_time).strftime("%Y-%m-%d, %H:%M:%S")})
        return up_shows

    def getArtistPastShowCount(self):
        return Shows.query.filter(self.id == Shows.artist_id, Shows.start_time < datetime.date.today()).count()

    def getArtistUpcomingShowCount(self):
        return Shows.query.filter(self.id == Shows.artist_id, Shows.start_time > datetime.date.today()).count()

    def makeStringForShowArtist(self):
        return {'id': self.id, 'name': self.name, 'genres': self.genres.split(','), 'city': self.city, 'state': self.state, 'phone': self.phone, 'website': self.website, 'facebook_link': self.facebook_link, 'seeking_venue': self.seeking_venue, 'seeking_description': self.seeking_description, 'image_link': self.image_link, 'past_shows': self.getArtistPastShows(), 'upcoming_shows': self.getArtistUpcomingShows(), 'past_shows_count': self.getArtistPastShowCount(), 'upcoming_shows_count': self.getArtistUpcomingShowCount()}

    def getArtistString(self):
        return {'id': self.id, 'name': self.name, 'genres': self.genres.split(','), 'city': self.city, 'state': self.state, 'phone': self.phone, 'website_link': self.website, 'facebook_link': self.facebook_link, 'seeking_venue': self.seeking_venue, 'seeking_description': self.seeking_description, 'image_link': self.image_link}


class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    artist_id = db.Column(
        db.Integer, db.ForeignKey('Artist.id'), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)

    def getShowString(self):
        venue = Venue.query.get(self.venue_id)
        artist = Artist.query.get(self.artist_id)
        return {'venue_id':venue.id,'venue_name':venue.name,'artist_id':artist.id, 'artist_name': artist.name, 'artist_image_link':artist.image_link, 'start_time':(
                self.start_time).strftime("%Y-%m-%d, %H:%M:%S")}


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    unique_places = Venue.query.distinct(Venue.city, Venue.state).all()
    for u in unique_places:
        data.append({'city': u.city, 'state': u.state, 'venues': [
            p.makeVenueStringWithShowCount() for p in Venue.query.filter(Venue.city == u.city, Venue.state == u.state).all()]})
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', None)
    venuesList = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
    c = len(venuesList)
    res = {
        "count": c,
        "data": [v.makeVenueStringForSearch() for v in venuesList]
    }
    return render_template('pages/search_venues.html', results=res, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venueObj = Venue.query.get(venue_id)
    data = venueObj.makeVenueStringForShowVenue()
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    try:
        venue_item = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.city.data,
            address=form.address.data,
            phone=form.phone.data,
            genre=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue_item)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

        # TODO: Complete this endpoint for taking a venue_id, and using
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
        return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artistsList = Artist.query.all()
    for a in artistsList:
        data.append({'id': a.id, 'name': a.name})
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', None)
    artistList = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()
    c = len(artistList)
    response = {
        "count": c,
        "data": [a.makeArtistStringForSearch() for a in artistList]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artistObj = Artist.query.get(artist_id)
    data = artistObj.makeStringForShowArtist()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artistObj = Artist.query.get(artist_id)
    artist = artistObj.getArtistString()
    form = ArtistForm(data=artist)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    try:
        artistObj = Artist.query.get(artist_id)
        artistObj.name = form.name.data
        artistObj.city = form.city.data
        artistObj.state = form.state.data
        artistObj.phone = form.phone.data
        artistObj.genre = json.dumps(form.genres.data)
        artistObj.facebook_link = form.facebook_link.data
        artistObj.image_link = form.image_link.data
        artistObj.website = form.website_link.data
        artistObj.seeking_venue = form.seeking_venue.data
        artistObj.seeking_description = form.seeking_description.data

        # artistObj = Artist(
        #     name=form.name.data,
        #     city=form.city.data,
        #     state=form.city.data,
        #     phone=form.phone.data,
        #     genre=form.genres.data,
        #     facebook_link=form.facebook_link.data,
        #     image_link=form.image_link.data,
        #     website=form.website_link.data,
        #     seeking_venue=form.seeking_venue.data,
        #     seeking_description=form.seeking_description.data
        # )
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venueObj = Venue.query.get(venue_id)
    venue = venueObj.getVenueString()
    form = VenueForm(data=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # try:
    #   venueObj = Venue.query.get(venue_id)
    form = VenueForm()
    try:
      venueObj = Venue.query.get(venue_id)
      venueObj.name = form.name.data
      venueObj.city = form.city.data
      venueObj.state = form.state.data
      venueObj.address = form.address.data
      venueObj.phone = form.phone.data
      venueObj.genre = json.dumps(form.genres.data)
      venueObj.facebook_link = form.facebook_link.data
      venueObj.image_link = form.image_link.data
      venueObj.website = form.website_link.data
      venueObj.seeking_talent = form.seeking_talent.data
      venueObj.seeking_description = form.seeking_description.data
      db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
    artistObj = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.city.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
      )
    db.session.add(artistObj)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    showList = Shows.query.all()
    for s in showList:
        data.append(s.getShowString())
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    try:
        showObj = Shows(start_time = form.start_time.data,
        artist_id = form.artist_id.data,
        venue_id=form.venue_id.data
        )
        db.session.add(showObj)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
