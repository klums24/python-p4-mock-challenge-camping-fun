from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import CheckConstraint

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship("Signup", back_populates="activity", cascade="all, delete-orphan")
    campers = association_proxy("signups", "camper")

    # Add serialization rules
    # serialize_rules = ("-signups.activity", "-signups.camper")
    serialize_only = ("id", "name", "difficulty")

    def __repr__(self):
        return f"<Activity {self.id}: {self.name}>"

    
    
class Camper(db.Model, SerializerMixin):
    __tablename__ = "campers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    signups = db.relationship("Signup", back_populates="camper", cascade="all, delete-orphan")
    activities = association_proxy("signups", "activity")
    # Add serialization rules
    serialize_rules = ("-created_at", "-updated_at", "-signups","-signups.camper", "signups.activity.id", "signups.activity.name", "signups.activity.difficulty")
    # Add validation
    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Camper needs to have a name")
        return name

    @validates("age")
    def validate_age(self, key, age):
        if age is None or not (8 <= age <= 18):
            raise ValueError("Camper's age needs to be between 8 and 18")
        return age
    
    def __repr__(self):
        return f"<Camper {self.id}: {self.name}>"

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }
        
    
class Signup(db.Model, SerializerMixin):
    __tablename__ = "signups"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id")) 
    # Add relationships

    camper = db.relationship("Camper", back_populates="signups")
    activity = db.relationship("Activity", back_populates="signups")

    # Add serialization rules
    serialize_only = ("id", "time", "activity_id", "camper_id")
    # serialize_rules = ("-activity.signups", "-camper.signups")

    # Add validation
    __table_args__ = (
        CheckConstraint("time >= 0 AND time <= 23", name="time_check"),
    )

    @validates("time")
    def validate_time(self, key, time):
        if time is not (0 <= time <= 23):
            raise AssertionError("Signup time must be between 0 and 23")
        return time
    
    def __repr__(self):
        return f"<Signup {self.id}>"

    def as_dict(self):
        return {
            "id": self.id,
            "time": self.time,
            "camper_id": self.camper_id,
            "activity_id": self.activity_id
        }

# add any models you may need.
