from flask import *
from flask_mysqldb import MySQL
import re
app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tha_davai_db'

mysql = MySQL(app)

@app.route('/', methods=['POST', 'GET'])
def index():
	# database connection
	cursor = mysql.connection.cursor()
	
	# SQL query for create data tables
	cursor.execute("""CREATE TABLE IF NOT EXISTS bookingApointment (
		id INT auto_increment,
		user_id INT,
		appointment_date DATE,
		desired VARCHAR(10),
		confirmation_requested_by VARCHAR(10),
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS user (
		id INT auto_increment,
		username VARCHAR(255),
		city  VARCHAR(255),	
		contact INT,
		email VARCHAR(255),
		password VARCHAR(255),
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS symptoms (
		id INT auto_increment,
		name VARCHAR(50),
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS doctor (
		id INT auto_increment,
		name VARCHAR(255),
		specialist  VARCHAR(255),	
		experince VARCHAR(255),
		location VARCHAR(20),
		degree VARCHAR(20),
		symptoms_id INT,	
		available_time DATETIME,
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS product (
		id INT auto_increment,
		name VARCHAR(50),
		description VARCHAR(50),
		price INT,
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS contact (
		id INT auto_increment,
		name VARCHAR(50),
		email VARCHAR(50),
		message TEXT,
		primary key (id)
	)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS cart (
		id INT auto_increment,
		qty INT,
		pro_id INT,
		user_id INT,
		primary key (id)
	)""")


	list_p = cursor.execute("SELECT * from product")
	list_product =  cursor.fetchall()
	print(list_product)
	mysql.connection.commit()
	if request.method == 'POST':
		username = request.form.get('username')
		city = request.form.get('city')
		contact = request.form.get('contact')
		email = request.form.get('email')
		password = request.form.get('password')
		cursor.execute('INSERT INTO user VALUES (%s,%s,%s,%s,%s,%s)',(username,city,contact,email,password))
		mysql.connection.commit()
		cursor.close()
		return 'Data added'
	return render_template('index.html', list_product=list_product)

@app.route('/login',methods=['GET','POST'])
def login():
	if request.method == 'POST':
		cursor = mysql.connection.cursor()
		username = request.form.get('username')
		password = request.form.get('password')
		print('======>> ',username, password);
		#cur = mysql.connection.cursor(MySQLdb.cursors.DictCufrom flask import Flask,render_template,request,session,url_for,redirectrsor)
		cursor.execute('SELECT * FROM user where username = %s and password = %s', (username,password,))
		user = cursor.fetchone()
		print('======? ',user)
		if user:
			#print(" -- ",users[0]);
			session['id'] = user[0]
			session['username'] = user[1]
			name = session['username']
			print("--",name) 
			return redirect('/')
		else:
			msg = 'Incorrect username/password.'
	return render_template('login.html')
		


@app.route('/logout', methods=['GET'])
def logout():
	del session['id']
	del session['username']

	return redirect('/')
@app.route('/booking', methods=['GET','POST'])
def bookingAppointment():
    	
		try:
	
			cursor = mysql.connection.cursor()
			user_id = session['id']
			fetch = cursor.execute("SELECT * from user where id=%s", (user_id,))

			fetch_user = cursor.fetchone()


			
			if request.method == 'POST':
				
				appointment_date = request.form.get('appointment_date')
				afternoon_desired = request.form.get('desired')
				confirmation_requested_by = request.form.get('confirmation_requested_by')
				procedure = request.form.get('procedure')
				print(appointment_date, afternoon_desired, confirmation_requested_by, procedure)
				cursor.execute('INSERT INTO bookingapointment (user_id,appointment_date,desired,confirmation_requested_by) VALUES (%s,%s,%s,%s)',(fetch_user[0], appointment_date, afternoon_desired , confirmation_requested_by,))
				mysql.connection.commit()
				cursor.close()
				return redirect('/')

			return render_template('bookingAppointment.html', msg='', fetch_user =fetch_user)
		except:
			message = Markup("<h2>First You have to Login</h2>")
			flash(message)
			return render_template('login.html', mesage = message)


	 
@app.route('/about', methods=['GET'])
def aboute():
	return render_template('about.html', msg='')
@app.route('/cart',methods=['GET','POST'])
def cart():
	cursor = mysql.connection.cursor()
	cursor.execute('SELECT p.name, p.price FROM cart as c JOIN product as p ON c.pro_id = p.id WHERE user_id = %s', (session['id'],))
	cartdetail = cursor.fetchone()
	
	print(cartdetail,"cartdetail")
    
	return render_template('cart.html',msg='', cartdetail = cartdetail)	

@app.route('/contact', methods=['GET','POST'])
def contact():
	message  = None
	cursor = mysql.connection.cursor()
	if request.method == 'POST':
		name = request.form.get('name')
		email = request.form.get('email')
		message = request.form.get('message')

		cursor.execute('Insert into contact (name, email, message) VALUES(%s,%s,%s)', (name,email,message))

		mysql.connection.commit()

		message = Markup("<h2>Your Message is Send</h2>")
		flash(message)
		return redirect('/contact')

	return render_template('contact.html' , message = message)

@app.route('/register',methods=['GET','POST'])
def register():
	msg=''
	
	if request.method == 'POST':
		cursor = mysql.connection.cursor()
		username = request.form.get('username')
		#birthdate = request.form.get('birthdate')
		city = request.form.get('city')
		contact = request.form.get('contact')
		email = request.form.get('email')
		password = request.form.get('password')

		#cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM user WHERE username = %s',(username,))
		users = cursor.fetchone()

		if users:
			msg = 'User account exist!'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'username contain only character and numbers.'
		elif not username or not email or not password:
			msg = 'Please fill the form.'
		else:
			cursor.execute('INSERT INTO user (username, city, contact, email, password) VALUES (%s,%s,%s,%s,%s)', (username, city, contact, email, password))
			mysql.connection.commit()
			# cursor.commit()
			msg = 'Successfully Registered...'
			return render_template('login.html') 

	elif request.method == 'POST':
		msg = 'Please fill!'
	return render_template('register.html',msg=msg) 


@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/shop')
def shop():
	cursor = mysql.connection.cursor()
	product_datas = cursor.execute('SELECT * from product')
	produst_lists = cursor.fetchall()
	print(produst_lists)
	return render_template('shop.html', produst_lists = produst_lists)

@app.route('/shop-detail/<int:id>',
methods=['GET','POST'])
def shop_detail(id):
	cursor = mysql.connection.cursor()
	get_product_detail = cursor.execute('SELECT * from product WHERE id=%s', (id,))
	Product_details = cursor.fetchone()

	if session.get('id') == False:
		return render_template('login.html', msg="" )
	if request.method == 'POST':
		
		pro_qty = request.form.get('productQty')
		print(session['id'],"userid")
		cursor.execute('INSERT INTO cart (qty, pro_id, user_id) VALUES (%s,%s,%s)', (pro_qty, Product_details[0],  session['id']))
		mysql.connection.commit()

	return render_template('shop-detail.html', Product_details = Product_details )
	
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
