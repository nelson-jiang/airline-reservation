from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import random

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       db='Airline Reservation',
                       charset='utf8mb4',
                       port = 8889,
                       cursorclass=pymysql.cursors.DictCursor)

## landing page
@app.route('/')
def hello():
     return render_template('landing.html')

""" Guest flight search uses c_search without the buy action """

# customer login redirection
@app.route('/c_login')
def c_login():
	return render_template('c_login.html')

# customer register redirection
@app.route('/c_register')
def c_register():
	return render_template('c_register.html')

#customer login authorization
@app.route('/c_loginAuth', methods=['GET','POST'])
def c_loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if (data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return render_template('c_homepage.html', cname=username)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('c_login.html', error=error)

#customer register authorization
@app.route('/c_registerAuth', methods=['GET', 'POST'])
def c_registerAuth():
    #grabs information from the forms
    username = request.form['email']
    name = request.form['name']
    password = request.form['password']
    

    building = request.form['building']
    street = request.form['street']
    city = request.form['city']

    state = request.form['state']
    phone_num = request.form['phone_num']
    DOB = request.form['dob']

    passport_num = request.form['passport_num']
    passport_country = request.form['passport_country']
    expiration_date = request.form['expiration_date']


    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'select * from customer where email = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('c_register.html', error=error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, name, password, building, street, city, state, phone_num, DOB, passport_num, passport_country, expiration_date))
        conn.commit()
        cursor.close()
        return render_template('c_login.html')


## customer homepage
@app.route('/c_homepage')
def c_homepage():
    if(session and session['username']):
        return render_template('c_homepage.html')
    else:
        return "Unauthorized Access"


## view my flights
@app.route('/c_view_flights')
def c_view_flights():
    
    cursor = conn.cursor()
    username = session['username']

    ## past flights query
    query = ("SELECT F.airline_name, F.flight_num, F.dept_date_time, T.ticket_ID, d.airport_name, a.airport_name, T.sold_price" +
             " FROM customer NATURAL JOIN buy NATURAL JOIN ticket as T NATURAL JOIN has NATURAL JOIN passenger NATURAL JOIN flight as F, arrival as a, departure as d" + 
             " WHERE customer.email = %s and F.airline_name = a.airline_name AND F.airline_name = d.airline_name" + 
             " AND F.flight_num = a.flight_num AND F.flight_num = d.flight_num AND F.dept_date_time = a.dept_date_time AND F.dept_date_time = d.dept_date_time AND F.dept_date_time < NOW()")
    cursor.execute(query, (username))
    data = cursor.fetchall()

    

    ## upcoming flights query
    query2 = ("SELECT F.airline_name, F.flight_num, F.dept_date_time, T.ticket_ID, d.airport_name, a.airport_name, T.sold_price" +
             " FROM customer NATURAL JOIN buy NATURAL JOIN ticket as T NATURAL JOIN has NATURAL JOIN passenger NATURAL JOIN flight as F, arrival as a, departure as d" + 
             " WHERE customer.email = %s and F.airline_name = a.airline_name AND F.airline_name = d.airline_name" + 
             " AND F.flight_num = a.flight_num AND F.flight_num = d.flight_num AND F.dept_date_time = a.dept_date_time AND F.dept_date_time = d.dept_date_time AND F.dept_date_time > NOW()")
    cursor.execute(query2,(username))
    data2 = cursor.fetchall()
    conn.commit()
    return render_template('c_view_flights.html', query_result = data, query2_result = data2)




## rating and comments
## view the form
@app.route('/rating_comments')
def rating_comments():

    airline_name = request.args.get('airline_name')
    flight_num = request.args.get('flight_num')
    dept_date_time = request.args.get('dept_date_time')

    return render_template('/rating_comments.html', airline_name = airline_name, flight_num = flight_num, dept_date_time = dept_date_time)

## save the rating and comment
@app.route('/save_rating_comments', methods = ['GET', 'POST'])
def save_rating_comments():

    rating = request.form['rating']
    comment = request.form['comment']

    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_date_time = request.form['dept_date_time']

    email = session['username']
    print(rating)
    print(comment)
    print(airline_name)
    print(flight_num)
    print(dept_date_time)
    print(email)
    cursor = conn.cursor()
    update = (' update passenger' +
              ' set rating = %s, comment = %s' +
              ' where email = %s and airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(update, (rating, comment, email, airline_name, flight_num, dept_date_time))
    conn.commit()
    cursor.close()
    return redirect('/c_view_flights')



## cancel trip
## view the form
@app.route('/cancel_trip')
def cancel():
    email = session['username']

    airline_name = request.args.get('airline_name')
    flight_num = request.args.get('flight_num')
    dept_date_time = request.args.get('dept_date_time')
    ticket_ID = request.args.get('ticket_ID')
    
    cursor = conn.cursor()
    query = (" select *" +
             " from customer natural join passenger" +
             " where email = %s and airline_name = %s and flight_num = %s and dept_date_time = %s")
    cursor.execute(query, (email, airline_name, flight_num, dept_date_time))
    data = cursor.fetchone()
    cursor.close()
    if (data):
        can_cancel = True
    else:
        can_cancel = False
    return render_template('cancel_trip.html', can_cancel = can_cancel, airline_name = airline_name, flight_num = flight_num, dept_date_time = dept_date_time, ticket_ID = ticket_ID)

## delete the trip if can cancel it
@app.route('/save_cancel_trip', methods = ['GET', 'POST'])
def save_cancel():
    email = session['username']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_date_time = request.form['dept_date_time']
    ticket_ID = request.form['ticket_ID']

    cursor = conn.cursor()
    del1 = 'delete from buy where email = %s and ticket_ID = %s'
    cursor.execute(del1, (email, ticket_ID))

    del2 = 'delete from passenger where email = %s and airline_name = %s and flight_num = %s and dept_date_time = %s'
    cursor.execute(del2, (email, airline_name, flight_num, dept_date_time))

    del4 = 'delete from has where ticket_ID = %s'
    cursor.execute(del4, (ticket_ID))

    del3 = 'delete from ticket where ticket_ID = %s'
    cursor.execute(del3, (ticket_ID))

    conn.commit()
    cursor.close()
    return redirect('/c_view_flights')



## Customer Search Flight
@app.route('/c_search', methods=['GET','POST'])
def c_search():

    # query for airport names
    cursor = conn.cursor();
    query = 'SELECT airport_name FROM airport ORDER BY airport_name'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    
    if (request.method == "POST"): 
        trip_type = request.form['trip_type']
        
        if (trip_type == "One Way"):

            # grab info from form
            dept_airport = request.form['dept_airport']
            dept_date = request.form['dept_date']
            dest_airport = request.form['dest_airport']

            cursor = conn.cursor()
            query = ("SELECT f.airline_name, f.flight_num, d.dept_date_time, d.airport_name, a.airport_name, f.base_price" + 
                        " FROM departure as d, arrival as a, flight as f" + 
                        " WHERE d.airline_name = f.airline_name AND f.airline_name = a.airline_name" + 
                        " AND d.dept_date_time = f.dept_date_time AND f.dept_date_time = a.dept_date_time AND d.flight_num = f.flight_num AND a.flight_num = f.flight_num" + 
                        " AND d.airport_name = %s AND DATE(d.dept_date_time) = %s AND a.airport_name = %s")
            cursor.execute(query, (dept_airport, dept_date, dest_airport))
            data2 = cursor.fetchall() # a List containing Dictionaries
            cursor.close()

            

            return render_template('c_search.html', one_way_result = data2, airports = data)

        elif (trip_type == "Round Trip"):

            dept_airport = request.form['dept_airport']
            dept_date = request.form['dept_date']
            dest_airport = request.form['dest_airport']
            ret_date = request.form['return_date']

            # Query for first flight
            cursor = conn.cursor()
            query = ("SELECT f.airline_name, f.flight_num, d.dept_date_time, d.airport_name, a.airport_name, f.base_price" + 
                        " FROM departure as d, arrival as a, flight as f" +
                        " WHERE d.airline_name = f.airline_name AND  f.airline_name = a.airline_name AND d.dept_date_time = f.dept_date_time AND f.dept_date_time = a.dept_date_time" + 
                        " AND d.flight_num = f.flight_num AND f.flight_num = a.flight_num" + 
                        " AND d.airport_name = %s AND DATE(f.dept_date_time) = %s AND a.airport_name = %s")
            cursor.execute(query, (dept_airport, dept_date, dest_airport))
            data3 = cursor.fetchall() # a List containing Dictionaries
            cursor.close()

            return render_template('c_search.html', departure_result = data3, return_date = ret_date, airports = data)
    else:
        return render_template('c_search.html', airports = data)


## purchase one way ticket
@app.route('/purchase_one_way')
def purchase_one_way():

    airline_name = request.args.get('airline_name')
    flight_num = request.args.get('flight_num')
    dept_date_time = request.args.get('dept_date_time')
    base_price = request.args.get('base_price')

    cursor = conn.cursor()

    # find num of tickets sold for this flight
    query1 = 'select count(*) as ticket_sold from flight natural join has where airline_name = %s and flight_num = %s and dept_date_time = %s'
    cursor.execute(query1, (airline_name, flight_num, dept_date_time))
    ticket_sold = cursor.fetchone()['ticket_sold']

    # find num of seat on this flight
    query2 = ('select num_of_seats from flight natural join is_on natural join airplane where airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(query2, (airline_name, flight_num, dept_date_time))
    tot_seat = cursor.fetchone()['num_of_seats']

    if (ticket_sold < tot_seat):
         can_buy = True
    else:
         can_buy = False

    return render_template('purchase.html', can_buy = can_buy, airline_name = airline_name, flight_num = flight_num, dept_date_time = dept_date_time, base_price = base_price)

## save purchase one way
@app.route('/save_purchase', methods = ['GET', 'POST'])
def save_purchase():
    email = session['username']

    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']
    dept_date_time = request.form['dept_date_time']
    base_price = request.form['base_price']

    print("DEBUG1")
    return_airline_name = request.form['return_airline_name']
    print("DEBUG" + return_airline_name)
    if(return_airline_name):
        print("DEBUG2")
        return_flight_num = request.form['return_flight_num']
        return_dept_date_time = request.form['return_dept_date_time']
        return_base_price = request.form['return_base_price']



    card_num = request.form['card_num']
    name_on_card = request.form['name_on_card']
    card_type = request.form['card_type']
    expiration_date = request.form['expiration_date']
    purchase_date_time = request.form['purchase_date_time']

    cursor = conn.cursor()
    query = "SELECT max(CAST(ticket_ID AS SIGNED INTEGER)) + 1 as ticket_ID FROM ticket"
    cursor.execute(query)
    ticket_ID = cursor.fetchone()['ticket_ID']
    print("TICKET ID" + str(ticket_ID))
    """ Insert the first leg """
    #insert into ticket table
    ins1 =  'insert into ticket values(%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins1, (ticket_ID, base_price, card_type, card_num, name_on_card, expiration_date, purchase_date_time))
    #insert into buy
    ins2 =  'insert into buy values(%s, %s)'
    cursor.execute(ins2, (ticket_ID, email))
    #insert into passenger
    ins3 =  'insert into passenger values(%s, %s, %s, %s, %s, %s)'
    cursor.execute(ins3, (email, airline_name, flight_num, dept_date_time, 0, 'NULL'))
    #insert into has
    ins4 = 'insert into has values(%s, %s, %s, %s)'
    cursor.execute(ins4, (ticket_ID, airline_name, flight_num, dept_date_time))

    """ Insert the second leg"""
    if(return_airline_name):

        query = "SELECT max(CAST(ticket_ID AS SIGNED INTEGER)) + 1 as ticket_ID FROM ticket"
        cursor.execute(query)
        return_ticket_ID = cursor.fetchone()['ticket_ID']

        #insert into ticket table
        ins5 =  'insert into ticket values(%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins5, (return_ticket_ID, return_base_price, card_type, card_num, name_on_card, expiration_date, purchase_date_time))
        #insert into buy
        ins6 =  'insert into buy values(%s, %s)'
        cursor.execute(ins6, (return_ticket_ID, email))
        #insert into passenger
        ins7 =  'insert into passenger values(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins7, (email, return_airline_name, return_flight_num, return_dept_date_time, 0, 'NULL'))
        #insert into has
        ins8 = 'insert into has values(%s, %s, %s, %s)'
        cursor.execute(ins8, (return_ticket_ID, return_airline_name, return_flight_num, return_dept_date_time))


    conn.commit()
    cursor.close()
    return redirect('/c_search')


# check return flights
@app.route('/check_return', methods = ['GET', 'POST'])
def check_return():

    # first leg information
    dept_airline_name = request.args.get('dept_airline_name')
    dept_flight_num = request.args.get('dept_flight_num')
    dept_dept_date_time = request.args.get('dept_dept_date_time')
    dept_airport_name = request.args.get('dept_airport_name')
    dest_airport_name = request.args.get('dest_airport_name')
    dept_base_price = request.args.get('dept_base_price')

    return_date = request.args.get('return_date')

    # query for return flight
    cursor = conn.cursor()
    query5 = ("SELECT f.airline_name, f.flight_num, d.dept_date_time, d.airport_name, a.airport_name, f.base_price" + 
              " FROM departure as d, arrival as a, flight as f" + 
              " WHERE d.airline_name = f.airline_name AND f.airline_name = a.airline_name" + 
              " AND d.dept_date_time = f.dept_date_time AND f.dept_date_time = a.dept_date_time" + 
              " AND d.flight_num = f.flight_num AND f.flight_num= a.flight_num" + 
              " AND d.airport_name = %s AND DATE(f.dept_date_time) = %s AND a.airport_name = %s")
    cursor.execute(query5, (dest_airport_name, return_date, dept_airport_name))
    return_result = cursor.fetchall()
    cursor.close()

    
    return render_template('c_search.html', dept_airline_name = dept_airline_name, dept_flight_num = dept_flight_num, dept_dept_date_time = dept_dept_date_time, dept_base_price = dept_base_price, return_result = return_result)

## purchase round trip
@app.route('/purchase_round')
def purchase_round():

    # second leg information
    return_airline_name = request.args.get('return_airline_name')
    return_flight_num = request.args.get('return_flight_num')
    return_dept_date_time = request.args.get('return_dept_date_time')
    return_base_price = request.args.get('return_base_price')

    # first leg information
    dept_airline_name = request.args.get('dept_airline_name')
    dept_flight_num = request.args.get('dept_flight_num')
    dept_dept_date_time = request.args.get('dept_dept_date_time')
    dept_base_price = request.args.get('dept_base_price')
    

    cursor = conn.cursor()

    """ validate both legs are purchasable """
    # find num of tickets sold for dept flight
    query1 = 'select count(*) as dept_ticket_sold from flight natural join has where airline_name = %s and flight_num = %s and dept_date_time = %s'
    cursor.execute(query1, (dept_airline_name, dept_flight_num, dept_dept_date_time))
    dept_flight_ticket_sold = cursor.fetchone()['dept_ticket_sold']

    # find num of seat on dept flight
    query2 = ('select num_of_seats from flight natural join is_on natural join airplane where airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(query2, (dept_airline_name, dept_flight_num, dept_dept_date_time))
    dept_flight_tot_seat = cursor.fetchone()['num_of_seats']

    # check dept flight is full or not
    dept_flight_not_full = dept_flight_ticket_sold < dept_flight_tot_seat

    # find num of tickets sold for return flight
    query3 = ('select count(*) as return_ticket_sold from flight natural join has where airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(query3, (return_airline_name, return_flight_num, return_dept_date_time))
    return_flight_ticket_sold = cursor.fetchone()['return_ticket_sold']

    # find num of seat on dept flight
    query4 = ('select num_of_seats from flight natural join is_on natural join airplane where airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(query4, (return_airline_name, return_flight_num, return_dept_date_time))
    return_flight_tot_seat = cursor.fetchone()['num_of_seats']

    # check return flight is full or not
    return_flight_not_full = return_flight_ticket_sold < return_flight_tot_seat

    if (dept_flight_not_full and return_flight_not_full):
         can_buy = True
    else:
         can_buy = False

    return render_template('purchase.html', can_buy = can_buy, airline_name = dept_airline_name, flight_num = dept_flight_num, dept_date_time = dept_dept_date_time, base_price = dept_base_price, return_airline_name = return_airline_name, return_flight_num = return_flight_num, return_dept_date_time = return_dept_date_time, return_base_price = return_base_price)


@app.route('/save_purchase_round')
def save_purchase_round():
    email = session['username']

    dept_airline_name = request.args.get('dept_airline_name')
    dept_flight_num = request.args.get('dept_flight_num')
    dept_dept_date_time = request.args.get('dept_dept_date_time')
    dept_base_price = request.args.get('dept_base_price')
    dept_sold_price = dept_base_price * 1.1
    dept_ticket_ID = 'T' + str(random.randint(100000000,999999999))


    return_airline_name = request.form['return_airline_name']
    return_flight_num = request.form['return_flight_num']
    return_dept_date_time = request.form['return_dept_date_time']
    return_ticket_ID = 'T' + str(random.randint(100000000,999999999))

    # query for the return flight's base price
    cursor = conn.cursor()
    query = ('select base_price from flight where airline_name = %s and flight_num = %s and dept_date_time = %s')
    cursor.execute(query, (return_airline_name, return_flight_num, return_dept_date_time))
    return_base_price = cursor.fetchone()
    return_sold_price = return_base_price * 1.1

    card_num = request.form['card_num']
    name_on_card = request.form['name_on_card']
    card_type = request.form['card_type']
    experiation_date = request.form['experiation_date']


    # insert dept flight
    #insert into ticket table
    ins1 =  ('insert into ticket values(%s, %s, %s, %s, %s, %s)')
    cursor.execute(ins1, (dept_ticket_ID, dept_sold_price, card_type, card_num, name_on_card, experiation_date))

    #insert into buy
    ins2 =  ('insert into buy values(%s, %s)')
    cursor.execute(ins2, (dept_ticket_ID, email))

    #insert into passanger
    ins3 =  ('insert into passenger values(%s, %s, %s, %s)')
    cursor.execute(ins3, (email, dept_airline_name, dept_flight_num, dept_dept_date_time))

    #insert into has
    ins4 =  ('insert into ticket values(%s, %s, %s, %s)')
    cursor.execute(ins4, (email, dept_airline_name, dept_flight_num, dept_dept_date_time))
    

    # insert return flight
    #insert into ticket table
    ins5 =  ('insert into ticket values(%s, %s, %s, %s, %s, %s)')
    cursor.execute(ins5, (return_ticket_ID, return_sold_price, card_type, card_num, name_on_card, experiation_date))

    #insert into buy
    ins6 =  ('insert into buy values(%s, %s)')
    cursor.execute(ins6, (return_ticket_ID, email))

    #insert into passanger
    ins7 =  ('insert into passenger values(%s, %s, %s, %s)')
    cursor.execute(ins7, (email, return_airline_name, return_flight_num, return_dept_date_time))

    #insert into has
    ins8 =  ('insert into ticket values(%s, %s, %s, %s)')
    cursor.execute(ins8, (email, return_airline_name, return_flight_num, return_dept_date_time))

    conn.commit()
    cursor.close()
    return redirect('/c_search')

#Logout Protocol
@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

""" 
Staff View Flight 
Staff Home            
""" 

@app.route('/staff_home', methods = ['GET', 'POST'])
def view_flight():

    start_date = None
    end_date = None
    dept_airport = None
    arrival_airport = None

    if(request.method=='POST'):

        start_date = request.form['start_date']
        end_date = request.form['end_date']

        dept_airport = request.form['dept_airport']
        arrival_airport = request.form['arrival_airport']

    # query for airport names
    cursor = conn.cursor();
    query = 'SELECT airport_name FROM airport ORDER BY airport_name'
    cursor.execute(query)
    airport_data = cursor.fetchall()
    
    
    query = ('SELECT flight.airline_name, flight.flight_num, flight.dept_date_time, flight.arr_date_time, departure.airport_name as dept_airport, arrival.airport_name as arrival_airport, flight.base_price, flight.status' +   
            ' FROM (flight NATURAL JOIN departure) JOIN arrival'  + # We CANNOT natural join because the airport in arrival and departure tables mean different things
            ' WHERE flight.airline_name = %s' +
            ' AND flight.airline_name = arrival.airline_name AND flight.flight_num = arrival.flight_num AND flight.dept_date_time = arrival.dept_date_time'  # join condition
            ) 
    
    parameters = (session['airline_name'],)
     
    if (start_date and end_date):
        query = query + ' AND flight.dept_date_time between %s and %s'
        parameters = parameters + (start_date, end_date)
    
    if (dept_airport):
        query = query + ' AND departure.airport_name = %s'
        parameters = parameters + (dept_airport,)

    if(arrival_airport):
        query = query + ' AND arrival.airport_name = %s'
        parameters = parameters + (arrival_airport,)


    if (not dept_airport and not arrival_airport and not start_date and not end_date): # default condition meaning none of the forms are filled

        default_condition = ' AND DATE(flight.dept_date_time) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)'
        query = query + default_condition
    

    
    
    cursor.execute(query, parameters)
    
    table_data = cursor.fetchall()

    cursor.close()
    

    return render_template('view_flight.html', flight_query_result = table_data, airports = airport_data, start_date = start_date, end_date = end_date, dept_airport = dept_airport, arrival_airport = arrival_airport   )



""" Edit Flight Status """

@app.route('/edit_status')
def edit_status():

    flight_num = request.args.get('flight_num')
    airline_name = request.args.get('airline_name')
    dept_date_time = request.args.get('dept_date_time')

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM flight WHERE flight_num = %s and airline_name = %s and dept_date_time = %s'
    cursor.execute(query, (flight_num, airline_name, dept_date_time))
    #stores the results in a variable
    data = cursor.fetchone() # a dictionary
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()


    return render_template('edit_status.html', x = data)

@app.route('/save_status', methods=['GET', 'POST'])
def save_status():
	
    new_status = None
    airline_name = None
    flight_num = None
    dept_date_time = None

    if(request.method=='POST'):
        new_status = request.form['status']
        airline_name = request.form['airline_name']
        flight_num = request.form['flight_num']
        dept_date_time = request.form['dept_date_time']


    cursor = conn.cursor();
    query = 'UPDATE flight SET status = %s WHERE airline_name = %s and flight_num = %s and dept_date_time = %s'
    cursor.execute(query, (new_status, airline_name, flight_num, dept_date_time))
    conn.commit()
    cursor.close()
        
    return redirect('/staff_home') # should redirect to '/staff_home'






""" View Ratings and Comments """
@app.route('/view_ratings')
def view_ratings():

    if(session and session['airline_name'] and session['username']): # authorize access


        # tells us which flight we are looking for
        flight_num = request.args.get('flight_num')                                         # get flight_id from request parameter
                                                                                            # In View_Flights, make sure flight_num and airline_name are passed in
        airline_name = request.args.get('airline_name')

        dept_date_time = request.args.get('dept_date_time')
	
        # query all of the records for particular flight
        # we are looking for info from one specific flight so we need to grab all the records of that flight
        cursor = conn.cursor()
        query = 'SELECT * FROM passenger WHERE flight_num = %s and airline_name = %s and dept_date_time = %s'
        cursor.execute(query, (flight_num, airline_name, dept_date_time))
        data = cursor.fetchall() # a list containing dictionaries
        cursor.close()

        # use a query to get the average rating
        cursor = conn.cursor()
        query2 = 'SELECT AVG(rating) as avg_rating FROM passenger WHERE flight_num = %s and airline_name = %s and dept_date_time = %s '
        cursor.execute(query2, (flight_num, airline_name, dept_date_time))
        data2 = cursor.fetchone() # a dictionary
        cursor.close()

        print("DATA")
        print(data)

        print("Data2")
        print(data2)


        return render_template('view_ratings.html', flight_num = flight_num, x = data, x2 = data2)

    else:
        return "Unauthorized Access"




""" Create Flight """

@app.route('/create_flight', methods = ['GET', 'POST'])
def create_flight():


    if(session and session['airline_name'] and session['username']): # Only allow authorized users 
                                                                     # We check authorized users based on if they have airline_name or not
        
        ''' query for all of the airport names and airplane_ID so for our dropdown menu we have the entire list of what we want'''
        cursor = conn.cursor();

        # query for airport names
        query = 'SELECT airport_name FROM airport ORDER BY airport_name'
        cursor.execute(query)
        data = cursor.fetchall()

        # query for airplane IDs
        query2 = 'SELECT airplane_ID FROM airplane WHERE airline_name = %s'
        cursor.execute(query2, (session['airline_name']))
        data2 = cursor.fetchall()

        cursor.close()

        airline_name = None
        flight_num = None
        dept_date_time = None
        arrival_date_time = None
        base_price = None
        status = None
        dept_airport =  None
        arrival_airport =  None
        airplane_id =  None

        # grab info from the form
        if(request.method=='POST'):
            airline_name = request.form['airline_name']
            flight_num = request.form['flight_num']
            dept_date_time = request.form['departure_date_time']
            arrival_date_time = request.form['arrival_date_time']
            base_price = request.form['base_price']
            status = request.form['status']

            dept_airport = request.form['dept_airport']
            arrival_airport =  request.form['arrival_airport']

            airplane_id = request.form['airplane']

    
            # validation --- make sure record is able to be inserted
            error = None
            if(arrival_date_time <= dept_date_time):

                error = "Error! Arrival Time Before Departure Time"

            elif(dept_airport == arrival_airport):

                error = "Error! Departure and Arrival Airport are Same"

            else:

                cursor = conn.cursor();
                query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND dept_date_time = %s'
                cursor.execute(query,(airline_name, flight_num, dept_date_time))
                data = cursor.fetchone()
                cursor.close()

                if(data): # error, a flight with (airline_name, flight_num, dept_date_time) already exists
                    error = "Error! Flight already exists"


            if(error):

    
                return render_template('create_flight.html', flight_num = flight_num, dept_date_time = dept_date_time, arrival_date_time = arrival_date_time, base_price = base_price, dept_airport = dept_airport, arrival_airport = arrival_airport, airplane_id = airplane_id, error = error, airports = data, airplanes = data2 ) 
       
    
            else: # flight can be created

                """
                insert into the database

                We need to insert into multiple tables

                All of these tables are related to (and affected) when we create a new flight

                """
                cursor = conn.cursor();

                # insert into flight table
                ins = 'INSERT INTO flight (airline_name, flight_num, dept_date_time, arr_date_time, base_price, status) VALUES (%s, %s, %s, %s, %s,%s)' # always use %s
                cursor.execute(ins, (airline_name, flight_num, dept_date_time, arrival_date_time, base_price, status))
                

                # insert into departure table
                ins2 = 'INSERT INTO departure (airport_name, airline_name, flight_num, dept_date_time) VALUES (%s, %s, %s, %s)' # always use %s
                cursor.execute(ins2, (dept_airport, airline_name, flight_num, dept_date_time))
                

                # insert into arrival table
                ins3 = 'INSERT INTO arrival (airport_name, airline_name, flight_num, dept_date_time) VALUES (%s, %s, %s, %s)' # always use %s
                cursor.execute(ins3, (arrival_airport, airline_name, flight_num, dept_date_time))
                

                # insert into is_on table
                ins4 = 'INSERT INTO is_on (airline_name, flight_num, dept_date_time, airplane_ID) VALUES (%s, %s, %s, %s)' # always use %s
                cursor.execute(ins4, (airline_name, flight_num, dept_date_time, airplane_id))


                conn.commit()
                cursor.close();


                
                return redirect('/staff_home')


        return render_template('create_flight.html', airports= data, airplanes = data2) # show user the form on create_flight.html

    else:
         return "Unauthorized Access"
    







""" View Report """

@app.route('/view_reports')
def view_reports():

    airline_name = request.args.get('airline_name') # In View_Flights, make sure airline_name are passed in
    return render_template('reports.html', airline_name = airline_name)


@app.route('/display_sales', methods=['GET', 'POST'])
def display_sales():

    airline_name = session['airline_name']

    option = None
    # grab time period from form
    if(request.method=='POST'):
        option = request.form['time_period']
    
    # query from database tables based on time period selected
    if(option == "date_range"):
        from_date = request.form['from']
        to_date =  request.form['to']

        cursor = conn.cursor()
        query = ("SELECT DATE_FORMAT(payment_date_time, '%%M-%%Y') as MONTH_YEAR, count(ticket_ID) as amount" +  # format the payment date to display month and year only   
                " FROM ticket natural join has" + 
                " WHERE airline_name = %s AND payment_date_time BETWEEN %s AND %s" + 
                " GROUP BY MONTH_YEAR") # GROUP BY month and year to show the amounts for each month along with its year
                                        # this MONTH_YEAR is referring to the column title named MONTH_YEAR above 

                # formatting notes:
                    # two %% if you want special formatting for dates
                    # put () around query if we want to "stack" the query
                      # use concatenation and double quotes
        cursor.execute(query, (airline_name, from_date, to_date))
        data = cursor.fetchall() # a list containing dictionaries
        cursor.close()
    
    elif (option == "month"):

        cursor = conn.cursor()
        query = ("SELECT DATE_FORMAT(payment_date_time, '%%M-%%Y') as MONTH_YEAR, count(ticket_ID) as amount" +    # format the payment date to display month and year only
                " FROM ticket natural join has" + 
                " WHERE airline_name = %s AND MONTH(payment_date_time) = MONTH(DATE_ADD(CURDATE(), INTERVAL -1 MONTH)) AND YEAR(payment_date_time) = YEAR(DATE_ADD(CURDATE(), INTERVAL -1 MONTH))" +
                " GROUP BY MONTH_YEAR") # condition is the month of payment date is one less than "now's" month and we also want the correct YEAR as well
                 # need GROUP BY because we are using aggregate function count



        cursor.execute(query, (airline_name))
        data = cursor.fetchall() # a list containing dictionaries
        cursor.close()

    
    elif (option == "year"): 

        cursor = conn.cursor()
        query = ("SELECT DATE_FORMAT(payment_date_time, '%%M-%%Y') as MONTH_YEAR, count(ticket_ID) as amount" +   # format the payment date to display month and year only 
                " FROM ticket natural join has" + 
                " WHERE airline_name = %s AND YEAR(payment_date_time) = YEAR(DATE_ADD(NOW(),INTERVAL -1 YEAR))" + # condition is the year of payment date is one less than "now's" year
                " GROUP BY MONTH_YEAR") 

        cursor.execute(query, (airline_name))
        data = cursor.fetchall() # a list containing dictionaries
        cursor.close()

    
    return render_template('reports.html', sales = data, airline_name = airline_name) # going back to SAME page reports.html
                                                                                      # difference is there's a table at the bottom


""" Add Airport """
@app.route('/add_airport', methods = ['GET', 'POST'])
def add_airport():

    if(session and session['airline_name'] and session['username']): # Checking authorization
                                                                # Only airline staff are allowed to access this function
        
        airport_name = None
        city =  None
        country = None
        type = None
        # grab information from the form
        if(request.method=="POST"):
            airport_name = request.form['airport_name']
            city =  request.form['city']
            country = request.form['country']
            type = request.form['type']
    

            #validation
            cursor = conn.cursor();
            query = 'SELECT * FROM airport WHERE airport_name = %s'
            cursor.execute(query,(airport_name))
            data = cursor.fetchone()
            cursor.close()

            if(data): # error, an airport with name already exists

                error = "Error! Airport already exists"
                
                return render_template('add_airport.html', airport_name = airport_name, city = city, country = country, type = type, error = error)
    
            else: # airport can be added

                # insert into the database
                cursor = conn.cursor();
                ins = 'INSERT INTO airport (airport_name, city, country, type) VALUES (%s, %s, %s, %s)' # always use %s
                cursor.execute(ins, (airport_name, city, country, type))
                conn.commit()
                cursor.close()

                # redirect to staff homepage
                return redirect('/staff_home')



        return render_template('add_airport.html') # give the user the form to add a new airport
    else:
        return "Unauthorized Access"



""" Add Airplane"""

@app.route('/add_plane')
def add_plane():

    if(session and session['airline_name'] and session['username']): # Only allow authorized users 
                                                                     # We check authorized users based on if they have airline_name or not
        return render_template('add_plane.html') # show user the form on add_plane.html
    else:
         return "Unauthorized Access"
    


@app.route('/save_added_plane', methods=['GET', 'POST'])
def save_added_plane():

    airline_name = None
    airplane_id = None
    num_of_seats = None
    manufacture = None
    age = None
    # grab info from the form
    if(request.method == "POST"):
        airline_name = request.form['airline_name']
        airplane_id = (request.form['airplane_id'])
        num_of_seats = (request.form['num_of_seats'])
        manufacture = request.form['manufacture']
        age = (request.form['age'])

    
    # validation --- make sure record is able to be inserted
    cursor = conn.cursor();
    query = 'SELECT * FROM airplane WHERE airplane_ID = %s'
    cursor.execute(query,(airplane_id))
    data = cursor.fetchone()
    cursor.close()

    if(data): # error, a plane with id already exists

        error = "Error! Plane already exists"

        return render_template('add_plane.html', error = error, airplane_id = airplane_id, num_of_seats = num_of_seats, manufacture = manufacture, age = age )
    
    else: # plane can be added

        # insert into the database
        cursor = conn.cursor();
        ins = 'INSERT INTO airplane (airline_name, airplane_ID, num_of_seats, manufacture, age) VALUES (%s, %s, %s, %s, %s)' # always use %s
        cursor.execute(ins, (airline_name, airplane_id, num_of_seats, manufacture, age))
        conn.commit()
        cursor.close()

        # redirect to confirmation page
        return redirect('/all_planes')

@app.route('/all_planes')
def all_planes():

    # Do a query to show all planes within the airline
    cursor = conn.cursor();
    query = 'SELECT * FROM airplane WHERE airline_name = %s'
    cursor.execute(query,(session['airline_name']))
    airplane_query_result = cursor.fetchall()
    cursor.close()

    return render_template('all_planes.html', airplane_query_result = airplane_query_result)


# Staff Login 
@app.route('/staff_login')
def staff_login():
    return render_template('staff_login.html', error = None)


# Staff Login Authorization
@app.route('/staff_login_auth', methods = ['GET', 'POST'])
def staff_login_auth():
      
    #grabs information from the login forms
    username = request.form['username']
    password = request.form['password']

    # searching the DB to see if a staff member with given username and password actually exists
    # this is the authentication part
    cursor = conn.cursor()
    query = 'SELECT * FROM staff NATURAL JOIN work WHERE username = %s AND password = %s' # join staff with work to get staff's airline info to put into session
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()

    error = None
    if(data): # the staff is legitimate --> the staff is allowed to proceed

        # creates a session for the the staff
        # input important info regarding staff into the session
        session['username'] = username
        session['airline_name'] = data['airline_name']
        return redirect('/staff_home') # Go to staff homepage 
    
    else: # the staff login is wrong --> tell user to try again

        # returns an error message to the html page
        error = 'Invalid username or password'
        return render_template('staff_login.html', error = error) # Go back to the login page but display error message this time



# Staff Register 
@app.route('/staff_register')
def staff_register():

    # query for airlines so we can do a drop down list in the Register page
    cursor = conn.cursor()
    query = 'SELECT airline_name FROM airline'
    cursor.execute(query)
    airlines = cursor.fetchall()
    cursor.close()

    return render_template('staff_register.html', airlines = airlines, error = None)



# Staff Register Authorization
@app.route('/staff_register_auth', methods = ['GET', 'POST'])
def staff_register_auth():

    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    first_name = request.form['first_name']
    last_name = request.form['last_name']

    email = request.form['email']
    phone = request.form['phone']

    dob = request.form['dob']

    airline_name = request.form['airline_name']
    
    # searching the DB to see if a staff member with given username already exists
    # this is the authentication part
    cursor = conn.cursor()
    query = 'SELECT * FROM staff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()

    error = None
    if(data): # If the previous query returns data, then user exists already

        # query for airlines so we can do a drop down list in the Register page
            # Put this here so if a user registers incorrectly, he can still see the dropdown list
        query = 'SELECT airline_name FROM airline'
        cursor.execute(query)
        airlines = cursor.fetchall()
        cursor.close()

        error = "This user already exists, please try again"
        return render_template('staff_register.html', error = error, airlines = airlines) # Go back to registration page but display error message
    
    else: # user doesn't exist yet, so registration is successful

        """ Insert our new user data into multiple tables """

        ins = 'INSERT INTO staff VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, dob))

        ins2 = 'INSERT INTO work VALUES(%s, %s)'
        cursor.execute(ins2, (airline_name, username))

        ins3 = 'INSERT INTO staff_email VALUES(%s, %s)'
        cursor.execute(ins3, (username, email))

        ins4 = 'INSERT INTO staff_phone VALUES(%s, %s)'
        cursor.execute(ins4, (username, phone))


        conn.commit()
        cursor.close()

        return redirect('/') # redirect to the landing page




# Staff Logout
@app.route('/staff_logout')
def staff_logout():

    # Removing the previously logged in staff's information from the session dictionary
    session.pop('username')
    session.pop('airline_name')

    return redirect('/') # sending back to landing page




app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)