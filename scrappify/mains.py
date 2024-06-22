from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
def scrape_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
        "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    # Request the HTML page from the web server based on the provided URL
    web_pages = requests.get(url, headers=headers)

    # Convert the HTML page into a BeautifulSoup object
    soup = BeautifulSoup(web_pages.content, "html.parser")

    # Find all the div tags containing reviews
    elements = soup.find_all("div", attrs={"class": "ZmyHeo"})

    # converting the html content in the list to string
    # string_list = [str(element) for element in elements]

    # Extract the text content from each div tag and append to the proto_list
    proto_list = [element.get_text(strip=True) for element in elements]

    # Convert the list of HTML elements to strings
    # string_list = [str(element) for element in elements]

    # Data cleaning: Remove specific words from each string in the list
    words_to_remove = ["READ MORE"]
    cleaned_list = [string for string in proto_list]
    for i, string in enumerate(cleaned_list):
        for word in words_to_remove:
            cleaned_list[i] = cleaned_list[i].replace(word, '')

    cleaned_list_final=[]
    for string in cleaned_list:
        cleaned_string=re.sub(r'^\d+', '', string).strip()
        cleaned_list_final.append(cleaned_string)

    return cleaned_list_final




def Analyze_Sentiment(Review_list):

    obj=SentimentIntensityAnalyzer()
    # Genertaes sentiment list of reviews
    sen_list=[]
    for i in Review_list:
        sen_dict=obj.polarity_scores(i)
        sen_list.append(sen_dict)
    print(sen_list)
    #Helps with graph generation
    rp = 0
    rn = 0
    rnu = 0
    for i in sen_list:
        if i.get("compound") > 0.1:
            rp = rp + 1
        elif i.get("compound") < -0.1:
            rn = rn + 1
        else:
            rnu = rnu + 1
    return rp,rn,rnu

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/",methods=['POST'])
def resultpg():
    url = request.form['urlToBeSent']
    # Split the URL at the product  part
    split_url = url.split('/p/')

    # Creating  the new URL
    new_url = split_url[0] + '/product-reviews/' + split_url[1]

    # Find the position where 'marketplace=FLIPKART' ends
    position = new_url.find('marketplace=FLIPKART') + len('marketplace=FLIPKART')

    #this contains the final url in a formatted manner
    final_url = new_url[:position]
    print(final_url)

    all_reviews = []
    num_pages = 3
    # Iterate through the specified number of pages
    for page_num in range(1, num_pages + 1):
        # Construct the URL for the current page
        current_url = f"{final_url}&page={page_num}"

        # Scrape the current page
        scraped_data = scrape_page(current_url)

        # Output the scraped data for the current page
        print(f"\nScraped data from Page {page_num}:")
        print(scraped_data)

        # adding all of the reviews into one single list
        all_reviews.extend(scraped_data)

    print("All Reviews\n")
    print(all_reviews)

    rp,rn,rnu = Analyze_Sentiment(all_reviews)


    data = { 'pos_num' : rp,
             'neg_num' : rn,
             'neu_num' : rnu
            }
    print(data)

    return render_template('resultpg.html', data = data)

@app.route("/home.html")
def homeFromResult():
    return render_template('home.html')


app.run(debug=True)

