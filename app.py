from flask import Flask, render_template, redirect, url_for, request
import requests
from textblob import TextBlob
import matplotlib.pyplot as plt
import io
import base64
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Still needed for session/flash messages

# Store votes (in-memory for demo purposes)
popular_articles = {}

def get_news_sentiment(topic):
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    # Check if 'articles' exists in the response
    if 'articles' not in data:
        print(f"Error: 'articles' key not found in the API response. Response: {data}")
        return []

    headlines = []
    for article in data['articles']:
        title = article['title']
        published_at = article['publishedAt']
        url_link = article['url']
        blob = TextBlob(title)
        polarity = blob.sentiment.polarity

        if polarity > 0.2:
            sentiment = "Bullish"
        elif polarity < -0.2:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        # Format the published date
        formatted_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")
        formatted_date = formatted_date.strftime("%B %d, %Y %I:%M %p")

        headlines.append({
            "title": title,
            "sentiment": sentiment,
            "published_at": formatted_date,
            "url": url_link
        })

    return headlines

def plot_sentiment_graph(headlines):
    sentiments = {'Bullish': 0, 'Bearish': 0, 'Neutral': 0}

    for article in headlines:
        sentiments[article['sentiment']] += 1

    labels = list(sentiments.keys())
    sizes = list(sentiments.values())
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    img_base64 = base64.b64encode(img.getvalue()).decode()

    return img_base64

@app.route('/')
def index():
    headlines = get_news_sentiment('bitcoin')
    graph = plot_sentiment_graph(headlines)
    return render_template("index.html", 
                           headlines=sorted(enumerate(headlines), key=lambda x: x[1]['published_at'], reverse=True),
                           graph=graph, 
                           popular_articles=popular_articles)

@app.route('/vote/<int:article_id>/<sentiment>', methods=['POST'])
def vote(article_id, sentiment):
    if article_id not in popular_articles:
        popular_articles[article_id] = {'bullish': 0, 'bearish': 0, 'neutral': 0, 'voted_users': set()}

    user_ip = request.remote_addr
    if user_ip not in popular_articles[article_id]['voted_users']:
        popular_articles[article_id][sentiment.lower()] += 1
        popular_articles[article_id]['voted_users'].add(user_ip)

    return redirect('/')

@app.route('/crypto')
def crypto():
    headlines = get_news_sentiment('crypto')
    graph = plot_sentiment_graph(headlines)
    return render_template("index.html", 
                           headlines=sorted(enumerate(headlines), key=lambda x: x[1]['published_at'], reverse=True),
                           graph=graph, 
                           popular_articles=popular_articles)

@app.route('/stocks')
def stocks():
    headlines = get_news_sentiment('stocks')
    graph = plot_sentiment_graph(headlines)
    return render_template("index.html", 
                           headlines=sorted(enumerate(headlines), key=lambda x: x[1]['published_at'], reverse=True),
                           graph=graph, 
                           popular_articles=popular_articles)

@app.route('/technology')
def technology():
    headlines = get_news_sentiment('technology')
    graph = plot_sentiment_graph(headlines)
    return render_template("index.html", 
                           headlines=sorted(enumerate(headlines), key=lambda x: x[1]['published_at'], reverse=True),
                           graph=graph, 
                           popular_articles=popular_articles)

if __name__ == '__main__':
    app.run(debug=True)
