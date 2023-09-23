import os
import tweepy as tw
from tweepy import Cursor
import sys
import shelve
import time

"""
Author: Sebastian Enger, M.Sc.
Date: 2023-09-22
Topic: Post about Ghostwriter Artikelschreiber.com on Twitter for related Twitter Posts
Web: http://www.unaique.net/ - http://www.artikelschreiber.com/

SEO Optimizer: Ghost Writer - Hausarbeiten schreiben mit KI|http://www.artikelschreiber.com/
SEO Tool: SEO Optimizer for Content Writing with Strong AI|http://www.artikelschreiber.com/en/
English ArtikelSchreiber Blog|http://www.unaique.net/blog/
ArtikelSchreiber Marketing Tools|http://www.artikelschreiber.com/marketing/
Text Generator deutsch - KI Text Generator|http://www.unaique.net/	
CopyWriting: Generator for Marketing Content by AI|http://www.unaique.net/en/
Recht Haben - Muster und Anleitung fuer Verbraucher|http://rechthaben.net/	
AI Writer|http://www.unaique.com/
"""

db                      = shelve.open("/home/unaique/twitter/tweeted.db")
counter                 = int(0)
# https://programtalk.com/python-examples/tweepy.Cursor/
# https://developer.twitter.com/en/docs/twitter-api/enterprise/rules-and-filtering/operators-by-product
# https://dev.to/twitterdev/a-comprehensive-guide-for-using-the-twitter-api-v2-using-tweepy-in-python-15d9
consumer_key_auth       = ''
consumer_secret_auth    = ''
access_token_auth       = ''
access_token_secret     = ''
bearer_token_auth       = ''

client                  = tw.Client(bearer_token=bearer_token_auth, consumer_key=consumer_key_auth, consumer_secret=consumer_secret_auth, access_token=access_token_auth, access_token_secret=access_token_secret )

search_for_en           = ['Text Generation', 'Text Generator', 'article generation', 'Article Generator', 'Text Writer', 'Text Writing', 'article writing']
search_for_de           = ['Text Generierung', 'Text Erstellung', 'Copywriting', 'Copywriter', 'Texter', 'Artikel Erstellung', 'Artikel erstellen']

text_ads_en             =  "use #ARTIKELSCHREIBER (https://www.artikelschreiber.com/en/) for free of costs article generation and '" # + search_for_de
text_ads_de             =  "nimm den gratis #ARTIKELSCHREIBER (https://www.artikelschreiber.com/) für die kostenlose Erstellung von Texten, Artikel, Blog Einträgen und '" # + search_for_de

hashtags_en             = "#TextGeneration #TextWriting #Copywriting #ArticleGenerator #TextGenerator #BlogArticle #BlogText #SEO #AI #NLP #NaturalLanguageProcessing"
hashtags_de             = "#Copywriter #SEO #Texte #Artikel #Autor #Schreiber #Texter #ArtikelSchreiben #ArtikelErstellen #KI"

for search in search_for_de:
    search              = str(search).strip()
    query               = search + ' lang:de'    # lang:de
    #query               = 'artikelschreiber.com lang:de'    # lang:de

    #try:
    tweets          = client.search_recent_tweets(query=query, expansions='author_id', max_results=100)
    users           = {u["id"]: u for u in tweets.includes['users']}

    # Get users list from the includes object
    for tweet in tweets.data:
        #print(tweet.id)
        if users[tweet.author_id]:
            user            = str(users[tweet.author_id])
            if user not in db:  # Wenn Eintrag in DB besteht, dann kein Tweet mehr senden!
                myUser      = "@"+user
                myTweet     = str(myUser+" "+text_ads_de+search+"'"+" "+hashtags_de)
                #print("TWEETING: '"+search+"' -> '",myTweet,"'")
                print("Tweeting:")
                print("\tSearch:"+search)
                print("\tContent:'"+myTweet+"'")
                print()
                db[user]     = '1'  #db[user]     = myTweet
                #client.create_tweet(quote_tweet_id='1460160633316552705', text=myTweet)
                client.create_tweet(quote_tweet_id=tweet.id, text=myTweet)
                counter = counter + 1
                time.sleep(7)
    #except Exception as a1:
    #    print("Error search for GERMAN tweets to handle")
    #    pass

for search in search_for_en:
    search              = str(search).strip()
    query               = search + ' lang:en'    # lang:de
    #query               = 'artikelschreiber.com lang:en'    # lang:de
    try:
        tweets          = client.search_recent_tweets(query=query, expansions='author_id', max_results=100)
        users           = {u["id"]: u for u in tweets.includes['users']}

        # Get users list from the includes object
        for tweet in tweets.data:
            #print(tweet.id)
            if users[tweet.author_id]:
                user            = str(users[tweet.author_id])
                if user not in db:  # Wenn Eintrag in DB besteht, dann kein Tweet mehr senden!
                    myUser      = "@"+user
                    myTweet     = str(myUser+" "+text_ads_en+search+"'"+" "+hashtags_en)
                    #print("TWEETING: '"+search+"' -> '",myTweet,"'")
                    print("Tweeting:")
                    print("\tSearch:"+search)
                    print("\tContent:'"+myTweet+"'")
                    print()
                    db[user]     = '1'  #db[user]     = myTweet
                    #client.create_tweet(quote_tweet_id='1460160633316552705', text=myTweet)
                    client.create_tweet(quote_tweet_id=tweet.id, text=myTweet)
                    counter = counter + 1
                    time.sleep(7)
    except Exception as a12:
        print("Error search for ENGLISH tweets to handle")
        pass

#print("I have sent this amount of tweets:", str(counter))
db.close()
sys.exit(0)
