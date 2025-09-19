from fastapi import FastAPI, HTTPException , Request
from pymongo import MongoClient
from fastapi.responses import RedirectResponse
from secrets import token_urlsafe
from pydantic import BaseModel
import validators
from pymongo.errors import ConnectionFailure
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from functools import wraps

#-------Imports for scraping web images-----#
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#---------------------------------------------------
app = FastAPI()


class Url(BaseModel):
    url: str

#--------------DataBase  connection --------------------
try:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    client.admin.command('ping') # check to see if server is available or not
    db = client["url_shortener"]
    collection = db["urls"]
    print("Successfully connected to MongoDB!")
except ConnectionFailure as e:
    print(f"Failed to connect to MongoDB: {e}")
    collection = None
#----------------------------------------------------------


# Decorator  to look up first and last click of given url 
def analytics_logger(collection):
    def decorator(func):
        global first_click
        now = datetime.now() #storing  timestamp at first click 
        first_click = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
        @wraps(func)
        async def wrapper(request: Request, short_id: str, *args, **kwargs):
            # Use the current time for storing last click time stamp
            
            current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p")
            # Find the document in the database
            query = {"_id": short_id}
            
            # storing the first click value
            collection.update_one(query, {"$set": {"first_click": first_click}})

            # Always update the last_click
            collection.update_one(query, {"$set": {"last_click": current_time}})
            
            # Call the original endpoint function to perform the redirection
            return await func(request, short_id, *args, **kwargs)
        return wrapper
    return decorator




# Function to scrape  dynamic web pages 
def scrape_dynamic_page(url):
    """
    Scrapes a single webpage with dynamic content using Selenium.
    """
    driver = None
        # Set up headless mode for Selenium to run without a visible browser window.
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize the WebDriver
        # You need to have a WebDriver (like chromedriver) installed and in your PATH.
    driver = webdriver.Chrome(options=options)
        
    print(f"Loading page with Selenium: {url}")
    driver.get(url)

        # Wait for the image element to be present on the page.
        # This gives time for JavaScript to load the content.
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'blur-fade-in'))
        )
        
        # Get the rendered HTML source after JavaScript has executed.
    page_source = driver.page_source

        # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

        # --- EXTRACTING DATA ---
        
        # Find the product image URL
    image_tag = soup.find('img', class_='blur-fade-in')
    product_image_url = image_tag.get('src') if image_tag and image_tag.get('src') else "N/A"

        # --- END OF DATA EXTRACTION ---
        
    product_data = {
            'image_url': product_image_url
        }

    return product_data



# -----------------Testing purpose ------------------
@app.get("/")
def home():
    return {"message": "This is home"}
#-----------------------------------------------------


# End point to shorten any given url 
@app.post("/short")
def url_shorter(request: Request, url: Url):
    """
    This endpoint takes a long URL, generates a short ID, and stores it in the database.
    - It validates the incoming URL.
    - If valid, it generates a unique ID using `token_urlsafe`.
    - It stores the unique ID and the original URL in the MongoDB collection.
    - It returns the full shortened URL to the user.
    """
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not available.")
    
    # Check if the URL is valid
    if validators.url(url.url):
        # Generate a short, URL token. This will be the unique ID.
        url_id = token_urlsafe(5)

        # Store the unique ID and the original URL.
        # store the ID itself for efficient lookup.
        # We also check if the generated ID already exists, though it's highly unlikely.
        if collection.find_one({"_id": url_id}):
            # Handle the unlikely case of a collision, maybe by regenerating the ID.
            raise HTTPException(status_code=500, detail="ID collision, please try again.")
        
        shortened_url = f"{request.base_url}{url_id}"
        collection.insert_one({"_id": url_id, "short_url":shortened_url , "long_url": url.url})
        return {"short_url": shortened_url}
    
    return {'msg': 'Invalid URL'}



#---------------------------------------------------------------------------
#Testing purpose----func to return and monitor document data 
@app.get('/data')
async def database():
    """
    This endpoint returns document data and it is for testing purpose .
    - It looks for  unique id , short link , long url , first click , last click .
    - If found, it  returns the data in json format.
    - If not found, it raises a 500 error.
    """
    if  collection is None :
        raise HTTPException(status_code=500 , detail="Database does not exist")

    document = collection.find({})
    data =[]
    for doc in document :
        data.append(doc)

    return {"database" : data}
#--------------------------------------------------------------------------



# Endpoint to redirect to original url  using unique id
@app.get("/{short_id}")
# Using decorator to store first and last click of shortened url
@analytics_logger(collection) 
async def redirect_url(request: Request , short_id: str):
    """
    This endpoint takes a short ID and redirects the user to the original long URL.
    - It looks up the unique ID in the database.
    - If found, it returns a RedirectResponse to the original URL.
    - If not found, it raises a 404 error.
    """
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not available.")

    # Look up the document using the unique ID from the URL.
    # We search the `_id` field, which is the unique token we generated.
    data = collection.find_one({"_id": short_id})

    # If no data is found for that ID, raise an HTTP 404 Not Found error.
    if not data:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Extract the original long URL from the data.
    long_url_data = data["long_url"]
    
    # Return a redirect response that sends the user to the original URL.
    return RedirectResponse(url=long_url_data)







#End point to scrape data from given url using unique id
@app.get("/scrape/{short_id}")
async def scrape_data(short_id:str):
    if collection is None:
        #If no  database exists
        raise HTTPException(status_code=500 , detail="Database not available")
    data =collection.find_one({"_id":short_id})
    if not data:
        # If no url present 
        raise HTTPException(status_code=404 , detail="URL not found")
    long_url =data["long_url"]
    response = requests.get(long_url)
    #return {"html-content": response.text}
    soup = BeautifulSoup(response.text ,'html.parser')
    # extracting brand details from the web page
    product_type =soup.find('div', class_='item-info').find('h2') if soup.find('div', class_='item-info') else None
    product_type_name = product_type.get_text(strip=True) if product_type else "N/A"

    #extracting product details from the web page
    product =soup.find('div' , class_='item-info').find(id='item-name') if soup.find('div' ,class_='item-info') else None
    product_name = product.get_text(strip=True) if product else "N/A"

    # extracting  image url from the web page
    img_value = scrape_dynamic_page(long_url)

    # extracting  product price from  the response body
    product_price=soup.find('div' , class_='pricing-info-wrapper').find(id='retail-price') if soup.find('div' , class_='pricing-info-wrapper') else None
    product_price_value = product_price.get_text(strip= True) if product_price else "N/A"


    return {"Brand": product_type_name ,
            "Product_name" : product_name,
            "Featured_image": img_value,
            "product_price": product_price_value}
