from flask import Flask, render_template, request, flash, redirect, session
import sys
import psycopg2
import datetime
app = Flask(__name__)

def register(result):
      cardNum = result['Username']
      Password = result['Password']
      cur.execute("SELECT u.password, u.id FROM user_ u WHERE u.cardNum = %s",(cardNum,))
      fetch = cur.fetchone()
      if fetch==None or Password != fetch[0]:
         cur.execute("SELECT m.password, m.id, m.firstname, m.lastname FROM mechanic m WHERE m.cardNum = %s",(cardNum,))
         fetch = cur.fetchone()
         if fetch==None or Password != fetch[0]:
            flash("This user doesn't exist")
            return redirect('/')
         session['userID'] = str(fetch[1])
         session['firstname'] = fetch[2]
         session['lastname'] = fetch[3]
         return "mechanic"
      session['cardNum'] = cardNum
      session['Password'] = Password
      session['userID'] = fetch[1]
      cur.execute("SELECT u.lastname FROM CHARGER_USER u WHERE u.id = %s",(session['userID'],))
      fetch = cur.fetchone()
      if fetch!=None:
         return "userWithCharge"
      return "user"

@app.route('/')
def student():
   return render_template('start.html')

@app.route('/signIn',methods = ['POST', 'GET'])
def signIn():
   if request.method == 'POST':
      return render_template('signIn.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      cur.execute("SELECT * FROM user_ WHERE cardNum=%s",(result['CreditCardNum'],))
      res = cur.fetchone()
      if res == None:      #if credit doesn't exist already
         cur.execute("SELECT max(id) from user_ LIMIT 1");
         try:
            max_ID =  int(cur.fetchone()[0])
         except:
            max_ID = 0
         new_ID = str(max_ID+1)
         newUsername = result['newUsername']
         newPassword = result['newPassword']
         CreditCardNum = result['CreditCardNum']
         cur.execute("INSERT INTO user_ (id, pseudo,password, cardNum) VALUES (%s, %s,%s,%s)",(new_ID, newUsername,newPassword, CreditCardNum))
         conn.commit()
         if result['firstName'] != "":
            firstName=result['firstName']
            name=result['name']
            phone=result['phone']
            road=result['road']
            roadNum=result['roadNum']
            codePostal=result['codePostal']
            commune=result['commune']
            cur.execute("INSERT INTO charger_user (id,firstname,lastname,phoneNum,road,roadNum,codePostal,commune) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(new_ID,firstName,name,phone,road,roadNum,codePostal,commune))
            conn.commit()
      return render_template("result.html",result = result)

@app.route('/connected',methods = ['POST', 'GET'])
def connected():
      hasCharger = "False"
      result = request.form
      if session.has_key('userType'):
         session['userType']=register(result)
      if session['userType']=="mechanic":
         return render_template("mechanic.html", firstname= session['firstname'], lastname= session['lastname'])
      elif session['userType']=="userWithCharge":
         hasCharger = "True"
      return render_template("connected.html",result = result, hasCharger = hasCharger)

@app.route('/consultScooters',methods = ['POST', 'GET'])
def consultScooters():
   users = ['maateen', 'nabin', 'shadd']
   return render_template('consultScooters.html', users=users)

@app.route('/infoScooters',methods = ['POST', 'GET'])
def infoScooters():
   cur.execute("SELECT numero, plainte, charge FROM scooters ")
   trips = cur.fetchall()
   return render_template('infoScooters.html', users=trips)

@app.route('/introPlainte',methods = ['POST', 'GET'])
def introPlainte():
   return render_template('introPlainte.html')

@app.route('/infoPlainte',methods = ['POST', 'GET'])
def infoPlainte():
   numTrottinette = request.form['numTrottinette']
   result = "Une demande a deja ete introduite ou la trottinette n'existe pas."
   cur.execute("SELECT s.plainte FROM scooters s WHERE s.numero=%s",(numTrottinette,))
   scooter = cur.fetchone()
   if scooter != None and not scooter[0] :
      cur.execute("UPDATE scooters SET plainte=%s WHERE numero=%s",("t",numTrottinette,))
      conn.commit()
      cur.execute("INSERT INTO reparations (scooter, userID, complainTime) VALUES (%s, %s,%s)",(numTrottinette, session['userID'], datetime.datetime.now().isoformat()))
      conn.commit()
      result = 'La demande de plainte pour la trottinette numero: '  + numTrottinette + ' a ete introduite.'
   return render_template('infoPlainte.html', result = result)

@app.route('/consultTrips',methods = ['POST', 'GET'])
def consultTrips():
   userID = session['userID']
   cur.execute("SELECT * FROM trips t WHERE t.userID=%s",(userID,))
   trips = cur.fetchall()
   return render_template('consultTrips.html', users=trips)

@app.route('/mechanic',methods = ['POST', 'GET'])
def mechanic():
   return render_template('mechanic.html')


if __name__ == '__main__':
   try:
      dbname=sys.argv[1]
      user=sys.argv[2]
   except:
      print("Arg error")
      exit()
   conn = psycopg2.connect("dbname="+dbname+" user="+user)
   cur = conn.cursor()
   app.secret_key = 'super secret key'
   app.run()   #host='0.0.0.0')
   cur.close()
   conn.close()