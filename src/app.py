"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorite
from sqlalchemy.orm import scoped_session

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def handle_hello():
    users = User.query.all()
    if users is None:
       raise APIException("No hay usuarios", status_code=400)
    users_serialized = list(map(lambda x: x.serialize(), users))
    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "users": users_serialized,
    }

    return jsonify(response_body), 200


@app.route('/users', methods= ['POST'])
def post_user():
    body= request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar informacion en el body", status_code=400)
    if "email" not in body:
        raise APIException("Debes enviar el campo email", status_code=400)
    if "password" not in body:
        raise APIException("Debes enviar tu contraseña", status_code=400)

    new_user = User(email = body['email'], password= body['password'], is_active= True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Completado", "new_user_info": new_user.serialize()})


@app.route("/planets", methods= ['GET'])
def get_planets():
    planets = Planets.query.all()
    planets_serialized = list(map(lambda x: x.serialize(), planets))
    return jsonify({"msg": "Completed", "planets": planets_serialized}) 


@app.route("/planets", methods=['PUT'])
def modify_planet():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar informacion en el body", status_code=400)
    if "id" not in body:
        raise APIException("Debes enviar el id del planeta a modificar", status_code=400)
    if "name" not in body:
        raise APIException("Debes enviar el nuevo nombre del planeta", status_code=400)
    single_planet = Planets.query.get(body['id'])
    single_planet.name = body['name']
    db.session.commit()
    return jsonify({"msg": "Completed"})


@app.route("/planets/<int:planet_id>", methods= ['GET'])
def get_a_planet(planet_id):
    single_planet = Planets.query.get(planet_id)
    if single_planet is None:
       raise APIException(f"No existe el planeta con el ID {planet_id}", status_code=400)
    
    response_body = {
        "msg": "Hello, this is your GET /planet response ",
        "planet_id": planet_id,
        "people_info": single_planet.serialize()
    }

    return jsonify(response_body), 200


@app.route("/planets/<int:planet_id>", methods= ['DELETE'])
def delete_planet(planet_id):
    single_planet = Planets.query.get(planet_id)
    if single_planet is None:
        raise APIException("El planeta no existe", status_code=400)
    
    db.session.delete(single_planet)
    db.session.commit()
    return jsonify({"msg": "Completed"})


@app.route("/people", methods= ['GET'])
def get_all_people():
    people = Characters.query.all()
    people_serialized = list(map(lambda x: x.serialize(), people))
    return jsonify({"msg": "Completed", "people": people_serialized})


@app.route('/people/<int:people_id>', methods=['GET'])
def handle_people(people_id):
    single_people = Characters.query.get(people_id)
    if single_people is None:
       raise APIException(f"No existe la persona con el ID {people_id}", status_code=400)
    
    response_body = {
        "msg": "Hello, this is your GET /people response ",
        "people_id": people_id,
        "people_info": single_people.serialize()
    }

    return jsonify(response_body), 200

@app.route("/users/favorites/<int:user_id>", methods = ['GET'])
def get_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id)
    if favorites is None:
         raise APIException(f"No existe el usuario con el ID {user_id}", status_code=404)
    response = list(map(lambda favorite: favorite.serialize(), favorites))

    response_body = {
        "msg": "Hello, this is your user's favorites response ",
         "user_id": user_id,
        "favorites": response
     }

    return jsonify(response_body), 200

#Add a new favorite planet to the current user with the planet id = planet_id

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    currentUser = 3
    request_body_favorite = request.get_json()
    
    favs = Favorite.query.filter_by(planets_id=planet_id).one_or_none()
    if favs is None:
        newFav = Favorite(
            user_id=currentUser, character_id= None,  planets_id=request_body_favorite["planets_id"])    
        db.session.add(newFav)
        db.session.commit()
        return jsonify("Planet added to favorites"), 200
    else:
        return jsonify("This planet has already been added to your favorites"), 400


#Add new favorite people to the current user with the people id = people_id
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    currentUser = 3
    request_body_favorite = request.get_json()
    favs = Favorite.query.filter_by(character_id= people_id).one_or_none()
    if favs is None:
        newFav = Favorite(
            user_id=currentUser, character_id= request_body_favorite["character_id"],  planets_id=None)   
        db.session.add(newFav)
        db.session.commit()
        return jsonify("Character added to favorites"), 200
    else:
        return jsonify("This character has already been added to your favorites"), 400


#Delete favorite planet with the id = planet_id


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    thatFav = Favorite.query.filter_by(planets_id= planet_id).one_or_none()
    if thatFav is None:
        raise APIException('Favorite not found', status_code=404)
    db_session = scoped_session(db.session)
    db_session.delete(thatFav)
    db_session.commit()

    return jsonify("Planet deleted from favorites"), 200


#Delete favorite people with the id = people_id
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    request_body = request.get_json()
    thatFav = Favorite.query.filter_by(character_id = people_id).one_or_none()
    if thatFav is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(thatFav)
    db.session.commit()

    return jsonify({"msg": "Character deleted from favorites"})






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)