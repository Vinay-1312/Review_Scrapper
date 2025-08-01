# doing necessary imports

from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import sqlite3
app = Flask(__name__)  # initialising the flask app with the name 'app'

#conn=sqlite3.connect('review.db')
#c=conn.cursor()
#searchString="xyz"

  #c.execute("SELECT * FROM review WHERE product= ?",(searchString,))

@app.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            conn=sqlite3.connect('review.db')
            c=conn.cursor()
            c.execute('''CREATE TABLE  IF NOT EXISTS {} (product varchar(255),Name varchar(255),Rating varchar(255),CommentHead varchar(255),Comment varchar(255))'''.format(searchString))#creating table if table does not exist

            
            
            c.execute("SELECT * FROM {} ".format(searchString))            #reviews=c.fetchall()
            reviews=c.fetchall();
            
            if len(reviews) > 0: # if there is a table with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews) # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
                uClient = uReq(flipkart_url) # requesting the webpage from the internet
                flipkartPage = uClient.read() # reading the webpage
                uClient.close() # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) # seacrhing for appropriate tag to redirect to the product link
                del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
                box = bigboxes[0] #  taking the first iteration (for demo)
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # extracting the actual product link
                prodRes = requests.get(productLink) # getting the product page from server
                prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) # finding the HTML section containing the customer comments

                reviews = [] # initializing an empty list for reviews
                #  iterating over the comment section to get the details of customer and their comments
                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text

                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment} # saving that detail to a dictionary
                    c.execute("insert into {} Values({},{},{},{},{})".format(searchString,searchString,name,rating,commentHead,custComment))
                    reviews.append(mydict) #  appending the comments to the review list
                return render_template('results.html', reviews=reviews) # showing the review to the user
        except Exception as e:
            return e
            
       
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(port=8000,debug=False) # running the app on the local machine on port 8000
