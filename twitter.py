from config import *
from utilities import *
import random
import tweepy

#driver.get(twitter_url)
products = list( db.products.find( {'published_at': False, 'discount_percentage' : {'$gt': 20} } ).limit(25) )
# personal information 
consumer_key =""
consumer_secret =""
access_token =""
access_token_secret =""
  
# authentication 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret) 
   
api = tweepy.API(auth)

for product in products:
    tweets = [f"الحق خصم {product['discount_percentage']}% على {product['product_title']} ",
         f"جوميا عاملالك خصم {product['discount_percentage']}% على {product['product_title']} ",
         f"متفكرش كتير خصم {product['discount_percentage']}% على {product['product_title']} ",
         f"لو حابب تشتري {product['product_title']} الحق بسرعة عشان جوميا موفرة عليك {product['discount_percentage']}% وهتشتريه ب{product['current_price']} بدل من {product['old_price']}  جنيه"
             ]
    tweet = random.choice(tweets)
    tweet = " ".join([ word for word in tweet.replace('\n', ' ').strip().split(' ')  if word.strip() != '' ] )
    tweet += '\n'
    tweet += f"{product['affiliate_url']}"
    try:
        print(tweet)
        if tweet != '\n':
            api.update_status(tweet)
        else:
            pass
    except tweepy.TweepError as e:

        print(e.reason)
    sleep(10)