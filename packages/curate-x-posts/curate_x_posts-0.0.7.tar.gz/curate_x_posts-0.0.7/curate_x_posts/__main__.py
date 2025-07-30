from pathlib import Path
import dotenv
import os
import pandas as pd
import argparse
import asyncio
from twikit import Client
from twikit.errors import TooManyRequests
import logging
import time
import csv
from datetime import datetime, timedelta

# instantiate twikit client
client = Client('en-US')

DEFAULT_COOKIE_PATH='x_cookies.json'

# Load environment variables from .env file
dotenv.load_dotenv()
USERNAME = os.getenv('X_USER')
EMAIL = os.getenv('X_EMAIL')
PASSWORD = os.getenv('X_PASS')

def setup_logger(level="DEBUG"):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        # level=logging.DEBUG,
        # level=level,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler())
    return logger

def store_data(data:list, output_path:Path):
    # Store the post IDs persistently
    try:
        keys = data[0].keys()
    except IndexError:
        logger.info("No data to save.")
        output_path.touch()
        return None

    logger.debug(f"WRITING DATA size {len(data)} to {output_path}")
    with open(output_path, mode='a+', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        if file.tell() == 0:
            logger.info(f"CREATING OUTPUT FILE {output_path}")
            writer.writeheader()
        # writer = csv.writer(file)
        
        writer.writerows(data)
        file.close()

def get_dict_from_tweet(tweet, iteration=0):
    tweet_dict = {
        "iteration": iteration,
        "id": tweet.id,
        "created_at": tweet.created_at,
        "created_at_dt": tweet.created_at_datetime,
        "user_name": tweet.user.name,
        "user_screen_name": tweet.user.screen_name,
        "user_id": tweet.user.id,
        "user_is_verified": tweet.user.is_blue_verified,
        "user_location": tweet.user.location,
        "user_followers_count": tweet.user.followers_count,
        "user_following_count": tweet.user.following_count,
        "user_can_dm": tweet.user.can_dm,        
        "user_listed_count": tweet.user.listed_count,
        "user_favourites_count": tweet.user.favourites_count,
        "user_statuses_count": tweet.user.statuses_count,
        "user_created_at": tweet.user.created_at,                        
        "text": tweet.full_text,
        "hashtags": tweet.hashtags,
        "urls": tweet.urls,
        "media": tweet.media,
        "bookmark_count": tweet.bookmark_count, # can be both pos/ negative sentiments
        "view_count": tweet.view_count,
        "like_count": tweet.favorite_count, # more certain to be pos sentiments
        "retweet_count": tweet.retweet_count,
        "quote_count": tweet.quote_count,
        "reply_count": tweet.reply_count,
        "lang": tweet.lang,
        "possibly_sensitive": tweet.possibly_sensitive,
        "in_reply_to": tweet.in_reply_to,
    }
    if tweet.is_quote_status and tweet.quote:
        tweet_dict["quoted_tweet"] = {
            "id": tweet.quote.id,
            "text": tweet.quote.full_text,
            }
    else:
        tweet_dict["quoted_tweet"] = None
    
    if tweet.place is not None:
        tweet_dict["place"] = {
            "id": tweet.place.id,
            "name": tweet.place.name,
            "full_name": tweet.place.full_name,
            "country": tweet.place.country,
            "country_code": tweet.place.country_code,
            "type": tweet.place.place_type,
            "centroid": tweet.place.centroid,
            "bounding_box": tweet.place.bounding_box
        }
    else:
        tweet_dict["place"] = None
    return tweet_dict

async def main(query, output_path, cookie_path=DEFAULT_COOKIE_PATH ):
    try: 
        logger.info("LOADED cookies to client")
        client.load_cookies(cookie_path)
    except FileNotFoundError:
        # avoid logging in multiple times as it is perceived as suspicious
        logger.info(f"MISSING cookie file {str(cookie_path)}. Logging in with credentials.")
        await client.login(
            auth_info_1=USERNAME ,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        client.save_cookies(cookie_path)
        logger.info(f"SAVED cookie file to {str(cookie_path)}")
    
    #######

    iteration = 0
    logger.info(f"SEARCH RESULTS PAGE {iteration}")

    start_time = time.time()
    tweets = await client.search_tweet(query, 'Latest')
    logger.info(f"found {len(tweets)} tweets")

    for tweet in tweets:
        logger.debug(f"FOUND tweet {tweet.id}")
        tweet_dict = get_dict_from_tweet(tweet, iteration=iteration)
        store_data(data=[tweet_dict], output_path=output_path)
    
    iteration = iteration + 1

    while True:
        loop_start_time = time.time()
        logger.info(f"SEARCH RESULTS PAGE {iteration}")
        try:
            more_tweets = await tweets.next()
        except TooManyRequests as e:
            
            logger.info(f"Request limit reached.")
            if e.headers:
                logger.debug(f"Header information: {e.headers}")
            if e.rate_limit_reset:
                logger.debug(f"Rate limit reset variable: {e.rate_limit_reset}")
            seconds_til_retry = (loop_start_time + 905) - time.time() #15min=900s rate limit
            logger.info(f"Waiting {seconds_til_retry} seconds.")
            await asyncio.sleep(seconds_til_retry)

        logger.info(f"found {len(more_tweets)} tweets")
        
        if len(more_tweets) == 0:
            break

        for tweet in more_tweets:
            logger.debug(f"FOUND tweet {tweet.id}")
            tweet_dict = get_dict_from_tweet(tweet, iteration=iteration)
            store_data(data=[tweet_dict], output_path=output_path)
        iteration = iteration + 1
        tweets = more_tweets
    
    end_time = time.time()
    logger.info(f"END OF SEARCH. Total time: {end_time - start_time}")

def parse_arguments():
    parser = argparse.ArgumentParser("X post curation via Twikit Scraper")

    parser.add_argument('-e', '--email',
                         default=None,
                         help="X email")
    parser.add_argument('-u', '--username',
                        default=None,
                        help="X username")
    parser.add_argument('-p', '--password',
                         default=None,
                         help="X password")

    parser.add_argument('-q', '--query',
                         default=None,
                         help="Search query")
    parser.add_argument('--lat',
                        default=None,
                        help="Latitude")
    parser.add_argument('--lon',
                        default=None,
                        help="Longitude")
    parser.add_argument('--radius-km',
                        default=10,
                        help="Radius of search area in kilometers. Default is 10.")
    parser.add_argument('--start-date',
                        default=None,
                        help="Start date of search in format YYYY-MM-DD.")
    parser.add_argument('--end-date',
                        default=None,
                        help="End date of search in format YYYY-MM-DD.")
    parser.add_argument('--days',
                        default=None,
                        type=int,
                        help="Number of days after start date to scrape for. Requires --start-date variable.")
    parser.add_argument('-o', '--out-dir',
                        default="",
                        help="CSV output directory, as a subfolder within out/.")
    parser.add_argument('--prefix',
                        default=None,
                        help="prefix")    
    parser.add_argument('-c','--cookie-path',
                        default=DEFAULT_COOKIE_PATH,
                        help=f"Path to {DEFAULT_COOKIE_PATH}")
    return parser.parse_args()
    
if __name__=="__main__":
    args = parse_arguments()
    logger = setup_logger(level="DEBUG")

    query = []
    
    geo_query_str = ''
    if None not in (args.lat, args.lat, args.radius_km):
        query.append(f"geocode:{args.lat},{args.lon},{args.radius_km}km")
        geo_query_str = f"{args.lat}_{args.lon}_{args.radius_km}km"
    
    if args.start_date:
        query.append(f"since:{args.start_date}")

    if args.end_date:
        query.append(f"until:{args.end_date}")
    
    if args.days and args.start_date:
        start_date_obj = datetime.strptime(args.start_date, "%Y-%m-%d")
        delta = timedelta(days=args.days)
        end_date_obj = start_date_obj + delta
        end_date = end_date_obj.strftime("%Y-%m-%d")
        query.append(f"until:{end_date}")
    
    if args.query: 
        query.append( args.query )
        
    if USERNAME is None:
        logger.info("Environment variables do not contain saved user credentials; using the ones provided in the argument list")
        USERNAME=args.username
        PASSWORD=args.password
        EMAIL=args.email

    query_str = " ".join(query)

    print(f"\n\nQUERY: '{query_str}'\n\n")
    logger.info(f"QUERY: '{query_str}'")
    
    out_dir =  Path("out/") / args.out_dir
    out_dir.mkdir(parents=True,exist_ok=True)

    if args.prefix is not None:
        args.prefix += '_' 
    
    out_filename = f"{args.prefix}{geo_query_str}_{time.strftime('%Y-%m-%dT%H:%M:%SZ')}.csv".replace(":", "")
    output_path = out_dir / out_filename
    
    if args.cookie_path:
        cookie_path = str(Path(args.cookie_path))

    asyncio.run(main(query=query_str, output_path=output_path, cookie_path=cookie_path))
