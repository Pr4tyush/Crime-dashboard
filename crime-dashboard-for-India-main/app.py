from functools import wraps
from flask import Flask, jsonify, make_response,render_template,url_for,request,redirect
from flask_jwt_extended import create_access_token,JWTManager, jwt_required
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from India import districtwise,clean_states,data01to14,multi_crime_plot,plot_map_any,states_to_ui
from predictions import children_prediction,children_crimes,children_states,children_years,pred_crime_plot,women_prediction,women_crimes,women_states,women_years

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
db=SQLAlchemy(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.debug = True
app.config['JWT_SECRET_KEY'] = 'asjfboaubfoubao'
jwt = JWTManager(app)
class User(db.Model):
    name=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(100),primary_key=True)
    password=db.Column(db.String(20),nullable=False)
    def __repr__(self) -> str:
        return f'Name: {self.name} , email {self.email}'

class Data(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	state=db.Column(db.String(200),nullable=False)
	district=db.Column(db.String(200),nullable=False)
	crime=db.Column(db.String(200),nullable=False)
	number=db.Column(db.Integer)
	year=db.Column(db.Integer)
	date_created=db.Column(db.DateTime,default=datetime.utcnow)
	def __repr__(self):
		return '<Task %r' % self.id
def protected_route(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Get access token from cookies
            access_token = request.cookies.get('access_token')
            print(access_token)
            # Verify access token
            if not access_token:
                return jsonify({"message": "Access token is missing"}), 401
        except Exception as e:
            return jsonify({"message": "An error occurred", "error": str(e)}), 500
    return wrapper
    
@app.route('/',methods=['GET','POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        # Query the database to check if the user exists
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # If user exists and password matches, set a cookie and redirect
            access_token = create_access_token(identity=email)
            response = make_response(render_template('index.html', email=email))
            response.set_cookie('access_token', access_token)
            return response
        else:
            # If user does not exist or password does not match, return an error
            return render_template('signin.html', error='Invalid email or password')        
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    else:
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        user = User(name=name, password=password,email=email)
        try:
            all_user=User.query.all()
            for users in all_user:
                print(users)
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            print(e)
            return render_template('signup.html',error='User Already Exists')
        access_token = create_access_token(identity=email)
        response = make_response(render_template('signin.html', success='Registration Success'))
        response.set_cookie('access_token', access_token)
        return response
@app.route('/index') 
def index():
	return render_template('index.html')

@app.route('/main')
def main():
	return render_template('main.html')
@app.route('/info')
def info():
	return render_template('info.html')

@app.route('/compare')
def compare():
	return render_template('compare.html')

@app.route('/graph')
def graph():
	return render_template('graph.html')

@app.route('/prediction')
def prediction():
	return render_template('prediction.html')

@app.route('/map')
def map():
	return render_template('map.html')

@app.route('/select')
def select():
	return render_template('select.html',data=[{'name':i} for i in ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh','Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand','Karnataka', 'Kerala', 'Lakshadweep', 'Madhya Pradesh','Maharashtra', 'Manipur', 'Mizoram', 'Nagaland','Odisha', 'Puducherry', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']])

@app.route('/selected',methods=['GET','POST'])
def selected():
	district_selected=request.form.get('district')
	crime_selected=request.form.get('crime') 
	districtwise(crime_selected,district_selected)
	return render_template('display.html')

@app.route('/multi_select')
def multi_select():
	return render_template('multiselect.html',data=[{'name':i} for i in data01to14['DISTRICT'].unique()],crimes=[{'name':i} for i in data01to14])

@app.route('/multi_selected',methods=['GET','POST'])
def multi_selected():
	district_selected=request.form.get('district')
	crimes_selected = request.form.getlist('crime')
	multi_crime_plot(district_selected,crimes_selected)
	return render_template('display_multi.html')

@app.route('/select_any')
def select_any():
	return render_template('select_any.html',crimes=[{'name':i} for i in data01to14])

@app.route('/selected_any',methods=['GET','POST'])
def selected_any():
	crime_selected = request.form.getlist('crime')
	plot_map_any(crime_selected)
	return render_template('display_any.html')

@app.route('/plotly_children')
def plotly_children():
	return render_template('plotly_children.html')

@app.route('/children_select')
def children_select():
	return render_template('select_pred_children.html',states=[{'name':i} for i in children_states],crimes=[{'name':i} for i in children_crimes],years=[{'name':i} for i in children_years])

@app.route('/children',methods=['POST','GET'])
def children():
	year = request.form.get("year")		
	crime = request.form.get("crime")
	state = request.form.get("state")
	y,years,output=children_prediction(state,year,crime)
	pred_crime_plot(state,crime,y,years)
	return render_template('display_multi.html')
	#return render_template('children.html',output=output,state=state, year=year,crime=crime,prediction = y,years = years)

@app.route('/women_select')
def women_select():
	return render_template('select_pred_women.html',states=[{'name':i} for i in women_states],crimes=[{'name':i} for i in women_crimes],years=[{'name':i} for i in women_years])

@app.route('/women',methods=['POST','GET'])
def women():
	year = request.form.get("year")		
	crime = request.form.get("crime")
	state = request.form.get("state")
	y,years,output=women_prediction(state,year,crime)
	pred_crime_plot(state,crime,y,years)
	return render_template('display_multi.html')

@app.route('/insert',methods=['POST','GET'])
def insert():
	if request.method=='POST':
		form_year=request.form['year']
		form_state=request.form['state']
		form_district=request.form['district']
		form_crime=request.form['crime']
		form_number=request.form['number']
		new_data=Data(state=form_state,district=form_district,crime=form_crime,number=form_number,year=form_year)
		if int(form_year)<=14:
			return 'no thanks'
		try:
			db.session.add(new_data)
			db.session.commit()
			return redirect('/insert')
		except:
			data=Data.query.order_by(Data.date_created).all()
			return render_template('insert.html',data=data)
	else:
		data_sorted=Data.query.all()
		return render_template('insert.html',data_sorted=data_sorted)

@app.route('/delete/<int:d>')
def delete(id):
	entry_to_delete=Data.query.get_or_404(id)
	try:
		db.session.delete(entry_to_delete)
		db.session.commit()
		return render_template('insert.html')
	except:
		return 'some problem'


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
with app.app_context():
    db.create_all()
if __name__ == "__main__":
	app.run(debug=True)