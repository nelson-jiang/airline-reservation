# airline-reservation

You’ll implement Air Ticket Reservation System as a web-based application. 

REQUIRED Application Use Cases (aka features): 

Home page when not logged-in: When the user is not logged-in, the following cases should be availablein the home page:
1. View Public Info: All users, whether logged in or not, cansearch for futureflights based on source city/airport name, destination city/airport name, departure date for one way (departure and returndates for round trip).2. Register: 2types of user registrations (Customer, andAirline Staff) optionvia formsas mentioned in the part 1 of the project.3. Login: 2types of user login (Customer, and Airline Staff). Usersenters their username (email addresswill be used as usernamefor customer))-x, and password-y, via forms on login page. This data is sent as POST parameters to the login-authentication component, which checks whether there is a tuple in the corresponding user’stable with username=xand the password = md5(y):A.If so, login is successful. A session is initiated with the member’s username stored as a sessionvariable.Optionally, you can store othersession variables. Control is redirected to a component that displays the user’s home page.B.If not, login is unsuccessful. A message is displayed indicating this to theuser.Oncea user has logged in, reservation systemshould display his/her home pageaccording to user’s role. Also, after otheractions or sequences of related actions, are executed, control will return to componentthat displays the home page. The home page should display an error message if the previous action was not successful. Some mechanism for the user to choose the use case he/she wants to execute:You may chooseto provide links to other URLsthat will present theinterfaces for other use cases,or you may include those interfaces directlyon the home page.Any other information you’d like to include:For example, you might want toshow customer's futureflights information on thecustomer's home page, or you may prefer to just show them when he/she does some ofthe following use cases.




Customer use cases: After logging in successfully a user (customer) may do any of the following use cases:

1. View Myflights: Provide various ways for the user to see flights information which he/she purchased. The default should be showingfor thefutureflights. Optionally you may include a way for theuser to specify a range of dates, specify destination and/or source airport name or city nameetc.
2.Search for flights: Search for futureflights(one way or round trip)based on source city/airport name, destination city/airport name, dates (departure or return)
3.Purchase tickets:Customer chooses a flight and purchase ticket for this flight, providing all the needed data, via forms.You mayfind it easier to implement this along with a use case to search for flights
4. Cancel Trip: Customer chooses a purchased ticket for a flight that will take place more than 24 hours in the future and cancel the purchase. After cancellation, the ticket will no longer belong to the customer. The ticket will be available again in the system and purchasable by other customers
5. Give Ratings and Comment on previous flights:Customer will be able to rate and comment on their previous flights (for which he/she purchased tickets and already took that flight) for the airline they logged in
6.Logout: The session is destroyed and a “goodbye” page or the login page isdisplayed.


Airline Staff use cases: After logging in successfully anairline staff may do any of the following use cases:

1. View flights: Defaults will be showing all the futureflightsoperated by the airline he/she works for the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline he/she works for based range of dates, source/destination airports/city etc. He/she will be able to see all the customers of a particular flight
2. Create new flights:He or she creates a new flight, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action.Defaults will be showing all the futureflightsoperated by the airline he/she works for the next 30 days
3. Change Status of flights:Heor she changes a flight status (from on-timeto delayed or vice versa) via forms
4. Add airplane in the system:He or she adds a new airplane, providing all theneeded data, via forms. The application should prevent unauthorized users from doing this action.In the confirmation page, she/he will beable to see all the airplanes owned by the airline he/she works for
5. Add new airport in the system:He or she adds a new airport, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action.
6. View flight ratings:Airline Staff will be able to see each flight’s average ratings and all the comments and ratings of that flight given by the customers
7. View reports: Total amounts of ticket sold based on range of dates/last year/last month etc.Month wise tickets sold in a barchart/table
8.Logout:The session is destroyed and a “goodbye” page or the login page isdisplayed.


Additional Requirements: You should implement Air ticket reservation systemas a web-based application.If you want to use a DBMSother than MySQL, SQLserver,Oracle, MongoDBor to use a programming language other than Python/Flask, Java/JDBC/Servlets, PHP,C#, node.js, or JavaScriptplease check with me first. You will need to bring the host computer to the demo/test session at the end of thesemester or make the application available remotely over the web. 

Enforcing complex constraints: Your air ticket reservation system implementation should prevent users from doing actions they are not allowed to do. For example, system should prevent users who are not authorized to do so from adding flight information. This should be done by querying the database to check whether the user is anairline staff or not before allowing him to create the flight. You may also use the interface to help the user to avoid violating the constraints. However, you should not rely solely on client-side interactions to enforce the constraint, since a user could bypass the client-side interface and send malicious http requests

Session Management: When a user logs in, a session should be initiated; relevant session variables should be stored. When the member logs out, the session should be terminated. Each component executed after the login component should authenticate the session and retrieve the user’s pid from a stored session variable. (If you’re using Python/Flask, you can follow the model in the Flask examples presented to do this.)

You must use prepared statements if your programming language supports them.(This is the style used in Flask; if you’re using PHP, use the MySQLi interface; if you’re using Java/JDBC, use the PreparedStmtclass.) If your programming language does not support prepared statements, Free form inputs (i.e., text entered through text boxes) that is incorporated into SQLstatements should be validated or cleaned to prevent SQL injection.

You should take measures to prevent cross-site scripting vulnerabilities, such as passing any text that comes from users through htmlspecialcharsor some such function, before incorporating it into the html that air ticket reservation system produces. 

The user interface should be usable, but it does not need to be fancy.For each type of users, you need to implement different home pages where youonly show relevant use cases for that type of users and you should not show/combine all the use cases in one page
