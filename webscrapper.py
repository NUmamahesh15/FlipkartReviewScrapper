from flask import Flask, render_template, request
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pymongo

app = Flask(__name__)

# Function to fetch the base url


def get_base_url_flipkart():
    return 'https://www.flipkart.com'

# Function to fetch the contents of the url page and returning the html parsed page


def get_soup(url):
    # Requesting the data from the url
    req_data = requests.get(url)
    # parsing the data from String to HTML format
    parse_data = BeautifulSoup(req_data.content, 'html.parser')
    # Returning the parsed data
    return parse_data

# Function to fetch the first product displayed in the search result


def fetch_product(product):
    # Concatenating the product to be searched with the base URL of flipkart
    flipkart_url = "https://www.flipkart.com/search?q=" + product
    # Getting the contents of the search page
    flipkart_html = get_soup(flipkart_url)
    # Finding the boxes containing the product details
    bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
    # deleting the boxes that are not required
    del bigboxes[0:3]
    # Fetching the first product among the list of all the products displayed
    box = bigboxes[0]
    # Fetching the link to the first product and concatenating it with the base flipkart url
    product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
    # Returning the product link for further processing
    return product_link


@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content']
        # searchString = searchString.replace(" ","")
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            db = dbConn['crawlerDB']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html',reviews=reviews)
            else:
                print("Testing")
                product_link = fetch_product(searchString)

                print(product_link)

                # Fetching the contents of the entire product page
                fetch_prod_page = get_soup(product_link)

                # Finding the div containing "view all reviews"
                fetch_all_reviews_page = fetch_prod_page.find('div', {'class': 'swINJg _3nrCtb'})

                # fetching the link to "all the reviews" page
                link_all_reviews = get_base_url_flipkart() + fetch_all_reviews_page.find_parent().get('href')
                print(link_all_reviews)

                # fetch the contents of the "all the reviews" page
                # review_page = get_soup(link_all_reviews)
                #
                # # Fetch all the reviews of that page
                # all_reviews = review_page.find_all('div', {'class': '_1PBCrt'})

                table = db[searchString]
                page=1
                reviews = []
                # looping through the pages
                while True:
                    #   Request reviews from the PAGE 1 initially, later the next pages
                    uri = link_all_reviews + '&page=' + str(page)
                    #   returns the content of the page
                    review_page = get_soup(uri)
                    #   get only the div containing all the reviews
                    all_reviews = review_page.find_all('div', {'class': '_1PBCrt'})
                    # looping over the reviews of the page
                    for commentbox in all_reviews:
                        try:
                            name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
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
                        # Creating dictionary to append it into the table
                        mydict = {
                            "Product": searchString,
                            "Name": name,
                            "Rating": rating,
                            "CommentHead": commentHead,
                            "Comment": custComment
                        }
                        # Append individual document/review into the table
                        x = table.insert_one(mydict)
                        # Appending individual reviews into the list
                        reviews.append(mydict)

                    # Fetch the navbar containing the pages, and check if the 'NEXT' is existing
                    find_nav_for_next_tag = review_page.find('nav', {'class': "_1ypTlJ"})
                    get_next_tag_text = find_nav_for_next_tag.find('span').get_text()

                    # If the 'Next' is present then fetch the link to the next page and concatenate it with the base url
                    # Else we terminate the while loop
                    if get_next_tag_text and page != 5:
                        page = page + 1
                    else:
                        break

                return render_template('results.html', reviews=reviews)
        except:
            return 'something is wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)