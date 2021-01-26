from flask import Flask,render_template,request,session,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import math
from flask_mail import Mail
from model_functs import generate_text,suggestions
from keras.models import load_model
import re
import os

export_path = os.path.join(os.getcwd(), 'models', 'shakespeare_bi_400_ud_loss_0.66')
shake_model=load_model(export_path)

def suggest(seed,model):
	suggested=[]
	suggested.append(suggestions(seed,model,346).replace('\n','\\n'))
	suggested.append(suggestions(seed,model,346//2).replace('\n','\\n'))
	suggested.append(suggestions(seed,model,346//4).replace('\n','\\n'))
	return suggested






with open('config.json','r') as c:
	params=json.load(c)['params']
local_server=True

app=Flask(__name__)
app.secret_key='super-secret-key'
app.config.update(
MAIL_SERVER='smtp.gmail.com',
MAIL_PORT='465',
MAIL_USE_SSL='True',
MAIL_USERNAME=params['gmail_user'],
MAIL_PASSWORD=params['gmail_pwd']
)
app.config['UPLOAD_FOLDER']=params['upload_location']
mail=Mail(app)

if (local_server==True):
	app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db=SQLAlchemy(app)

class Posts(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), unique=False, nullable=False)
	slug=db.Column(db.String(21))
	content = db.Column(db.String(120), unique=False, nullable=False)
	date=db.Column(db.String(50))
	img_file=db.Column(db.String(12))
	tagline=db.Column(db.String(50))


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    phone_no=db.Column(db.String(50))
    email = db.Column(db.String(50), unique=False, nullable=False)
    msg=db.Column(db.String(50))

@app.route('/',methods=['POST','GET'])
def home():
	#PAGINATION LOGIC
	text=''
	return render_template('index.html',params=params,text=text)

@app.route('/generate_poem',methods=['POST','GET'])
def generate_poem():
	#PAGINATION LOGIC
	text=''
	if(request.method=='POST'):
		print('successfully')
		author=request.form.get('author')
		len_text=request.form.get('len_text')
		seed=request.form.get('seed')
		print(request.form)
		if(author=='Shakespeare'):
			text=generate_text(seed, int(len_text), shake_model, 344)
			text=text.split('\n')
			if len(text[-2])//2>len(text[-1]):
				text='\n'.join(text[:-1])
			else:
				text='\n'.join(text)
	return render_template('generative.html',params=params,text=text)




@app.route('/about')
def about():
	return render_template('about.html',params=params)

@app.route('/contact',methods=['GET','POST'])
def contact():
	if (request.method=='POST'):
		name=request.form.get('name')
		email=request.form.get('email')
		msg=request.form.get('msg')
		phone=request.form.get('phone')	
		entry=Contacts(name=name,phone_no=phone,email=email,msg=msg)
		db.session.add(entry)
		db.session.commit()
		mail.send_message('Send message from '+name,
			sender=email,recipients=[params['gmail_user']],
			body=msg+phone)
	return render_template('contact.html',params=params)


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
	if request.method=='POST':
		results=[]
		seed = request.form.get('seed')
		print(seed)
		print(type(seed))
		results=suggest(seed, shake_model)
		return jsonify(results)


@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
	if('user' in session and session['user']==params['admin_user']):
		posts=Posts.query.all()
		return render_template('dashboard.html',params=params,posts=posts)
	if(request.method=='POST'):
		u_name=request.form.get('uname')
		pwd=request.form.get('pwd')
		if(u_name==params['admin_user'] and pwd==params['userpass']):
			#set the session variable
			session['user']=u_name
			posts=Posts.query.all()
			return render_template('dashboard.html',params=params,posts=posts)
	else:
		return render_template('login.html',params=params)


@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
	post=Posts.query.filter_by(slug=post_slug).first()

	return render_template('post.html',params=params,post=post)
@app.route('/suggestive', methods=['POST','GET'])
def suggestive():
	if request.method=='POST':
		seed = request.form.get('seed')
		print(type(seed))
		result=suggest(seed, shake_model)
		seed=seed.replace('\n','\\n')
		
		return render_template('post.html',params=params,results=list(set(result)),seed_text=seed)
	else:
		return render_template('post.html',params=params,results=['','',''],seed_text='')



if __name__ == "__main__":
	app.run(debug=True)
#,host='0.0.0.0',port=int(os.environ.get('PORT',8080))
#     app.run(debug=False)
