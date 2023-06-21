#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort, g
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict() for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        data = request.get_json()
        new_camper = Camper(**data)
        try:
            db.session.add(new_camper)
            db.session.commit()
            response = jsonify(new_camper.to_dict())
            return make_response(response, 201)

        except Exception as e:
            return make_response({"error": str(e)})

api.add_resource(Campers, "/campers")

class CamperById(Resource):
    def get(self, id):
        if camper := db.session.get(Camper, id):
            return make_response(camper.to_dict(only=("id", "age", "name", "signups")), 200)
        else:
            return make_response({"error": "Camper does not exist"}, 404)

    def patch(self, id):
        try:
            camper = db.session.get(Camper, id)
            if not camper:
                return make_response(jsonify({"error": "404: Camper not found"}), 404)
            data = request.get_json()
            for key, value in data.items():
                setattr(camper, key, value)
            db.session.commit()
            return make_response(jsonify(camper.to_dict()), 200)
        except (Exception, IntegrityError) as e:
            return make_response(jsonify({"error": str(e)}), 400)
        
    def delete(self, id):
        try:
            camper = db.session.get(Camper, id)
            db.session.delete(camper)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except Exception as e:
                
                return make_response(jsonify({"error": "404: Camper not found"}), 404)
api.add_resource(CamperById, "/campers/<int:id>")

class Activities(Resource):

    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(activities, 200)
    
    def post(self):
        try:
            data = request.get_json()
            activity = Activity(**data)
            db.session.add(activity)
            db.session.commit()
            response = jsonify(activity.to_dict())
            return make_response (response, 201)
        except (Exception, IntegrityError) as e:
            return make_response(jsonify({"error": str(e)}), 400)
    
api.add_resource(Activities, "/activities")

class ActivityById(Resource):

    def get(self,id):
        if activity := Activity.query.get(id):
            return make_response(activity.to_dict(), 200)
        else:
            abort(404, f"No activity exists with id {id}")

    def delete(self, id):
        activity = Activity.query.get_or_404(id)
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        else:
            make_response({"error": "Activity not found"}, 404)
    
api.add_resource(ActivityById, "/activities/<int:id>")

class Signups(Resource):
    def get(self):
        signups = [signup.to_dict() for signup in Signup.query.all()]
        return make_response(signups, 200)
    
    def post(self):
        data = request.get_json()
        camper_id = data.get('camper_id')
        activity_id = data.get('activity_id')

        if camper_id is None or activity_id is None:
            abort(400, 'Validation error')

        # Check if the camper and activity exist
        camper = Camper.query.get(camper_id)
        activity = Activity.query.get(activity_id)

        if camper is None or activity is None:
            abort(400, 'Validation error')

        # Create the signup
        signup = Signup(camper=camper, activity=activity)
        db.session.add(signup)
        db.session.commit()

        # Return the related activity data
        response = jsonify(activity.to_dict())
        response.headers.set("Content-Type", "application/json")
        return response
api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
