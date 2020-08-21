# FlipkartReviewScrapper
A simple flipkart review scraper that fetches the reviews of a product searched by the user. 
By default this fetches the reviews of the first product found in the result of the search. 
There are certain constraints in the first version like, the user should enter the exact name of the product, and the reviews is limited to first 5 pages. 
Later versions will aim to allow the user to enter the desired number of pages of the reviews.

Requirements:
Python 3, PyCharm, MongoDB
libraries to support this application is present in the requirements.txt file.

1. index.html display the search area for the user to enter the product name.
2. result.html displays the result of the search.
3. If the user enters the wrong product name, or if the product does not exist, page displays "Something went wrong" error.
4. If the product is found and the reviews are already existing, it fetches the reviews from the table and displays it to the user.
5. If the product is found and the reviews are not existing in the db, it adds all the reviews into the mongodb collection(name of the product) and displays it to the user.
