#!/usr/bin/python37all
import cgi
import json

# Retrieve Data from HTML
data = cgi.FieldStorage()
parents_message = data.getvalue('message') # slider value
alarm_time = data.getvalue('alarm') # selected LED
data = {"message":parents_message, "alarm":alarm_time} # store values

# Store data in json/txt
with open('alarm.txt', 'w') as f:  
  json.dump(data,f) # dump data

# New .html page
print('Content-type:text/html\n\n')

print('<html>')
print('<form action="/cgi-bin/alarm.py" method="POST">')
print('<body style="background-color:powderblue;">')
print('<h1 style="font-family:Tahoma;color:yellow;">Little Timmy\'s Wake-Up Alarm</h1>')
print('<p style="font-family: Tahoma">')
# Selecting Message to Send
print('<input type="radio" name="message" value="smile" checked> Smiley Face <br>')
print('<input type="radio" name="message" value="silly"> Silly Face <br>')
print('<input type="radio" name="message" value="heart"> Heart <br> <br>')
# Selecting Alarm Time
print('<label for="alarm">Select a time for your child\'s alarm to sound:</label> <br>')
print('<input type="time" id="alarm" name="alarm"> <br> <br> <br>')
# Submit
print('<input type="submit" value="Submit Changes" ')
print('style="background-color:yellow;font-family: Tahoma">')
print('</form>')
print('</html>')