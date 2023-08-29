from flask import Flask,render_template,request, redirect
import requests
import random
import string
import sqlite3
from datetime import timezone
import time


app=Flask(__name__)

def checker(lurl):     #function to check if the url entered is a valid url
            try:
                  response = requests.get(lurl)   
                  return True  
            except requests.exceptions.RequestException as e:
                  return False

@app.route('/', methods=["GET","POST"])
def home():
      if(request.method=='GET'):
        return(render_template("home.html"))
      else:
            lurl=request.form.get("urlhtml")
            seclimit=int(request.form.get("tlh"))*360+int(request.form.get("tlm"))*60+int(request.form.get("tls"))
            al=int(request.form.get("al"))
            nl=request.form.get("choice")
            print(nl)
            if(nl=="no limit"):
                  al=-1
                  seclimit=2147483646
            if(al==0):
                  al=-1
            else:
                  al=al+1
            
            check=checker(lurl)
            if(seclimit==0):
                  seclimit=2147483646    #maximum time possible in unix if user wants to generate a immortal code
            else:
                  seclimit=int(time.time())+seclimit
            if(check):
                  ourl=lurl
                  eid=str(random.randint(0,9))+random.choice(string.ascii_letters)+str(random.randint(0,9))+random.choice(string.ascii_letters)+str(random.randint(0,9))+str(random.randint(0,9))+random.choice(string.ascii_letters)+str(random.randint(0,9))+random.choice(string.ascii_letters)+str(random.randint(0,9))
                  conn = sqlite3.connect('urldb.sqlite')
                  cursor=conn.cursor()
                  cursor.execute("CREATE TABLE IF NOT EXISTS urlscodes (original_url TEXT NOT NULL, code TEXT PRIMARY KEY NOT NULL, al INTEGER NULL, timelimit INTEGER NOT NULL DEFAULT (strftime('%s', 'now')))")
                  cursor.execute("INSERT INTO urlscodes VALUES (?, ?,?, ?)",(ourl, eid, al,seclimit))
                  conn.commit()
                  conn.close
                  nurl="http://127.0.0.1:5000/"+eid
                  return(render_template("response.html",ourl=ourl,nurl=nurl,eid=eid))
            else:
                  return(render_template("invalid.html"))
            

@app.route('/<string:shortcode>') 
def red(shortcode):    
      conn = sqlite3.connect('urldb.sqlite')
      cursor = conn.cursor()
      currtime=int(time.time())
      query="SELECT * FROM urlscodes WHERE code like '"+shortcode+"'"
      cursor.execute(query)
      row = cursor.fetchone()
      if(row):
            if(currtime<=row[3] and row[2]!=0):
                  nal=row[2]-1
                  if(nal==0):
                        cursor.execute('delete from urlscodes where code like"'+shortcode+'"')
                        conn.commit()
                        conn.close()
                        return render_template("invalid.html")
                  else: 
                        cursor.execute("update urlscodes set al=? where code= ?",(nal,shortcode))
                        conn.commit()
                        conn.close()
                        original_url=row[0]
                        return redirect(str(original_url))
            else:
                  conn.close()
                  return render_template("invalid.html")
      else:
            conn.close()
            return(render_template("invalid.html"))

if __name__ == "__main__":
    app.run(debug=True)