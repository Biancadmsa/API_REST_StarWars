from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship("Favorite", back_populates="user" )

    def __repr__(self):
        return f"User with email {self.email} and id {self.id}"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }



class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    terrain = db.Column(db.String(50), unique=False, nullable=False)
    rotation_period = db.Column(db.Integer, unique=False, nullable=False)
    diameter = db.Column(db.Integer, unique=False, nullable=False)
    """ favorite = db.relationship('Favorite', back_populates='planet') """

    # Print planet info
    def __repr__(self):
        return f"Planet {self.name} with ID {self.id}"

    def serialize(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "terrain": self.terrain,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter
        }


class Characters(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    hair_color = db.Column(db.String(50), unique=False, nullable=False)
    height = db.Column(db.Integer, unique=False, nullable=False)
    mass = db.Column(db.Integer, unique=False, nullable=False)
    """ favorite = db.relationship('Favorite', back_populates='character') """


    #Print characters info
    def __repr__(self):
        return f"Character {self.name} with ID {self.id}"
    
    def serialize(self):
        return {
            "id" : self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "height": self.height,
            "mass": self.mass
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user= db.relationship("User", back_populates= "favorites")
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=True)
    planets_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)

    def serialize(self):
        return {
            "id" : self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planets_id": self.planets_id
        }


     