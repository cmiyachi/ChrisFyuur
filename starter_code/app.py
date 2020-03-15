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

from sqlalchemy_utils import create_database, database_exists
import config
import traceback
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy.orm.exc import NoResultFound

from flask_migrate import Migrate
from flask_moment import Moment
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# TODO: connect to a local postgresql database  DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE
    def seed_data(self):
        Venue.query.delete()

        data1 = {
            "name": "The Musical Hop",
            "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],

            "address": "1015 Folsom Street",
            "city": "San Francisco",
            "phone": "123-123-1234",
            "website": "https://www.themusicalhop.com",
            "facebook_link": "https://www.facebook.com/TheMusicalHop",
            "seeking_talent": True,
            "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
            "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
        }
        data2 = {
            "name": "The Dueling Pianos Bar",
            "genres": ["Classical", "R&B", "Hip-Hop"],
            "address": "335 Delancey Street",
            "city": "New York",
            "phone": "914-003-1132",
            "website": "https://www.theduelingpianos.com",
            "facebook_link": "https://www.facebook.com/theduelingpianos",
            "seeking_talent": False,
            "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
        }
        data3 = {
            "name": "Park Square Live Music & Coffee",
            "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
            "address": "34 Whiskey Moore Ave",
            "city": "San Francisco",
            "phone": "415-000-1234",
            "website": "https://www.parksquarelivemusicandcoffee.com",
            "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
            "seeking_talent": False,
            "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
        }

        venues = [data1,data2,data3]

        for data in venues:
            venue = Venue(**data)
            db.session.add(venue)

        db.session.commit()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Venue %r>' % self

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'genres': self.genres.split(','),
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'website': self.website,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description
                }

    @property
    def serialize_with_upcoming_shows_count(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'website': self.website,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'num_shows': Show.query.filter(
                    Show.start_time > datetime.datetime.now(),
                    Show.venue_id == self.id)
                }

    @property
    def serialize_with_shows_details(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'upcoming_shows': [show.serialize_with_artist_venue for show in Show.query.filter(
                    Show.start_time > str(datetime.datetime.now()),
                    Show.venue_id == self.id).all()],
                'past_shows': [show.serialize_with_artist_venue for show in Show.query.filter(
                    Show.start_time < str(datetime.datetime.now()),
                    Show.venue_id == self.id).all()],
                'upcoming_shows_count': len(Show.query.filter(
                    Show.start_time > str(datetime.datetime.now()),
                    Show.venue_id == self.id).all()),
                'past_shows_count': len(Show.query.filter(
                    Show.start_time < str(datetime.datetime.now()),
                    Show.venue_id == self.id).all())
                }

    @property
    def filter_on_city_state(self):
        return {'city': self.city,
                'state': self.state,
                'venues': [v.serialize_with_upcoming_shows_count
                           for v in Venue.query.filter(Venue.city == self.city,
                                                       Venue.state == self.state).all()]}


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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    
    def seed_data(self):
        Artist.query.delete()

        data1 = {
            "name": "Guns N Petals",
            "genres": ["Rock n Roll"],
            "city": "San Francisco",
            "state": "CA",
            "phone": "326-123-5000",
            "website": "https://www.gunsnpetalsband.com",
            "facebook_link": "https://www.facebook.com/GunsNPetals",
            "seeking_venue": True,
            "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
            "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
        }
        data2 = {
            "name": "Matt Quevedo",
            "genres": ["Jazz"],
            "city": "New York",
            "state": "NY",
            "phone": "300-400-5000",
            "facebook_link": "https://www.facebook.com/mattquevedo923251523",
            "seeking_venue": False,
            "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"

        }
        data3 = {
            "name": "The Wild Sax Band",
            "genres": ["Jazz", "Classical"],
            "city": "San Francisco",
            "state": "CA",    
            "phone": "432-325-5432",
            "seeking_venue": False,
            "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
        }

        artists = [data1,data2,data3]

        for data in artists:
            artist = Artist(**data)
            db.session.add(artist)

        db.session.commit()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Artist %r>' % self

    @property
    def serialize_with_shows_details(self):
        print('***&&&')
        print(self.image_link)
        print('***&&&')
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'genres': self.genres,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'upcoming_shows': [show.serialize_with_artist_venue for show in Show.query.filter(
                    Show.start_time > str(datetime.datetime.now()),
                    Show.artist_id == self.id).all()],
                'past_shows': [show.serialize_with_artist_venue for show in Show.query.filter(
                    Show.start_time < str(datetime.datetime.now()),
                    Show.artist_id == self.id).all()],
                'upcoming_shows_count': len(Show.query.filter(
                    Show.start_time > str(datetime.datetime.now()),
                    Show.artist_id == self.id).all()),
                'past_shows_count': len(Show.query.filter(
                    Show.start_time < str(datetime.datetime.now()),
                    Show.artist_id == self.id).all())
                }

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'genres': self.genres,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                }



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    venue = db.relationship(
        'Venue', backref=db.backref('shows', cascade='all, delete'))
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    artist = db.relationship(
        'Artist', backref=db.backref('shows', cascade='all, delete'))
    
    def seed_data(self):
        Show.query.delete()

        data = [{
            "venue_id": 1,
            "artist_id": 1,
            "start_time": "2019-05-21T21:30:00.000Z"
        }, {
            "venue_id": 3,
            "artist_id": 2,
            "start_time": "2019-06-15T23:00:00.000Z"
        }, {
            "venue_id": 3,
            "artist_id": 3,
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "artist_id": 1,
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 2,
            "artist_id": 3,
            "start_time": "2035-04-15T20:00:00.000Z"
        }]

        for show in data:
            show = Show(**show)
            db.session.add(show)

        db.session.commit()


    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Show %r>' % self

    @property
    def serialize(self):
        print('+++++++++++++++++++++++')
        print(self.start_time) #.strftime("%m/%d/%Y, %H:%M:%S"))
        return {'id': self.id,
                'start_time': self.start_time, #.strftime("%m/%d/%Y, %H:%M:%S"),
                'venue_id': self.venue_id,
                'artist_id': self.artist_id
                }

    @property
    def serialize_with_artist_venue(self):
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&")
        # print(self.start_time) #.strftime("%m/%d/%Y, %H:%M:%S"))
        print([v.serialize for v in Venue.query.filter(Venue.id == self.venue_id).all()][0])
        print("AFTER&&&&&&&&&&&&&&&&&&&&&&&&&&")
        return {'id': self.id,
                'start_time': self.start_time, #.strftime("%m/%d/%Y, %H:%M:%S"),
                'venue': [v.serialize for v in Venue.query.filter(Venue.id == self.venue_id).all()][0],
                'artist': [a.serialize for a in Artist.query.filter(Artist.id == self.artist_id).all()][0]
                }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    print('&*&*&*&*&*&*&*&*****************')
  #  print(value.strftime("%m/%d/%Y, %H:%M:%S"))
    print('xxxxxxxxxxxxxxx')
    print(value)    
    return(value)

def format_datetime2(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#-----------------------------------------------------------------------------------
#  Used to populate the database with initial data
#-----------------------------------------------------------------------------

@app.route('/seed')
def seed():

    venue = Venue()
    venue.seed_data()

    artist = Artist()
    artist.seed_data()

    show = Show()
    show.seed_data()
    return redirect(url_for('index'))
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.  DONE
  unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [ucs.filter_on_city_state for ucs in unique_city_states]
  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"  DONE
  """ response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  } """
  search_term = request.form.get('search_term', None)
  venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
  count_venues = len(venues)
  response = {
      "count": count_venues,
      "data": [v.serialize for v in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id DONE
 
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  venues = Venue.query.filter(Venue.id == venue_id).one_or_none()

  if venues is None:
      abort(404)

  # data = [v.serialize_with_upcoming_shows_count for v in venues][0]
  data = venues.serialize_with_shows_details
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead  DONE
  # TODO: modify data to be the data object returned from db   DONE

  # on successful db insert, flash success
  venue_form = VenueForm(request.form)

  try:
      new_venue = Venue(
          name=venue_form.name.data,
          genres=','.join(venue_form.genres.data),
          address=venue_form.address.data,
          city=venue_form.city.data,
          state=venue_form.state.data,
          phone=venue_form.phone.data,
          facebook_link=venue_form.facebook_link.data,
          image_link=venue_form.image_link.data)
          # TODO:  Add website???

      new_venue.add()
      # on successful db insert, flash success
      flash('Venue ' +
            request.form['name'] +
            ' was successfully listed!')
  except Exception as ex:
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be listed.')
      traceback.print_exc()
  # TODO: on unsuccessful db insert, flash an error instead.  DONE
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using DONE
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
      venue_to_delete = Venue.query.filter(Venue.id == venue_id).one()
      venue_to_delete.delete()
      flask("Venue {0} has been deleted successfully".format(
          venue_to_delete[0]['name']))
  except NoResultFound:
      abort(404)
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database DONE
  artists = Artist.query.all()
  data = [artist.serialize_with_shows_details for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".  DONE
  """ response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  } """
  search_term = request.form.get('search_term', None)
  artists = Artist.query.filter(
      Artist.name.ilike("%{}%".format(search_term))).all()
  count_artists = len(artists)
  response = {
      "count": count_artists,
      "data": [a.serialize for a in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  DONE
  artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

  if artist is None:
      abort(404)

  data = artist.serialize_with_shows_details
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_form = ArtistForm()

  artist_to_update = Artist.query.filter(
      Artist.id == artist_id).one_or_none()
  if artist_to_update is None:
      abort(404)

  artist = artist_to_update.serialize
  form = ArtistForm(data=artist)
  # TODO: populate form with fields from artist with ID <artist_id> DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing DONE
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
      artist = Artist.query.filter_by(id=artist_id).one()
      artist.name = form.name.data,
      artist.genres = json.dumps(form.genres.data),  # array json
      artist.city = form.city.data,
      artist.state = form.state.data,
      artist.phone = form.phone.data,
      artist.facebook_link = form.facebook_link.data,
      artist.image_link = form.image_link.data,
      artist.update()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id> DONE
  venue_form = VenueForm()

  venue_to_update = Venue.query.filter(Venue.id == venue_id).one_or_none()
  if venue_to_update is None:
      abort(404)

  venue = venue_to_update.serialize
  form = VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes DONE
  form = VenueForm(request.form)
  try:
      venue = Venue.query.filter(Venue.id==venue_id).one()
      venue.name = form.name.data,
      venue.address = form.address.data,
      venue.genres = '.'.join(form.genres.data),  # array json
      venue.city = form.city.data,
      venue.state = form.state.data,
      venue.phone = form.phone.data,
      venue.facebook_link = form.facebook_link.data,
      venue.image_link = form.image_link.data,
      venue.update()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead DONE
  # TODO: modify data to be the data object returned from db insertion DONE
  artist_form = ArtistForm(request.form)
  genres=','.join(artist_form.genres.data)
  name=artist_form.name.data    
  city=artist_form.city.data
  state=artist_form.state.data
  phone=artist_form.phone.data
  facebook_link=artist_form.facebook_link.data
  image_link=artist_form.image_link.data
  print(genres)
  print(name)
  print(city)
  print(state)
  print(phone)
  print(facebook_link)
  print(image_link)
  try:
      new_artist = Artist(
          name=artist_form.name.data,
          genres=','.join(artist_form.genres.data),
          city=artist_form.city.data,
          state=artist_form.state.data,
          phone=artist_form.phone.data,
          facebook_link=artist_form.facebook_link.data,
          image_link=artist_form.image_link.data)
      print(new_artist.genres)
      new_artist.add()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as ex:
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be listed.')

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
  # TODO: replace with real venues data. DONE
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = [show.serialize_with_artist_venue for show in shows]
  print(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead DONE
  show_form = ShowForm(request.form)
  try:
      show = Show(
          artist_id=show_form.artist_id.data,
          venue_id=show_form.venue_id.data,
          start_time=show_form.start_time.data
      )
      show.add()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except Exception as e:
      flash('An error occurred. Show could not be listed.')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. DONE
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    # app.run()
    manager.run()
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
