import logging
import re
import chart
import pandas as pd
from team_data import team_data
from praw import Reddit
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta


SUBREDDIT = 'reddevils'
CSV_FILE = 'data_points.csv'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
NUM_POSTS = 30
TEST_SUB = 'testingground4bots'

# configuring logging
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logging.info('Program Starts.')


# create reddit instance
def create_reddit_instance():
    load_dotenv()
    logging.info('Environment variable loaded.')

    reddit = Reddit(client_id=getenv('client_id'),
                    client_secret=getenv('client_secret'),
                    user_agent=getenv('user_agent'),
                    username=getenv('user_name'),
                    password=getenv('password'))

    reddit.validate_on_submit = True
    logging.info('Reddit instance created.')
    return reddit


# get subreddit
def get_subreddit(sub, reddit):

    subreddit = reddit.subreddit(sub)
    logging.info(f'Subreddit {sub} loaded.')
    return subreddit


# fetch all comments from subreddit's latest posts and return comments made in last 24 hours
def get_all_comments(subreddit):
    all_comments = []
    current_time = datetime.utcnow()
    past_24_hours = current_time - timedelta(hours=24)
    logging.info('Datetime object created for past 24 hours.')

    for submission in subreddit.new(limit=NUM_POSTS):
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            comment_time = datetime.utcfromtimestamp(comment.created_utc)
            if comment_time > past_24_hours:
                all_comments.append(comment.body)

    logging.info('All comments list created.')
    logging.info(f'{len(all_comments)} comments fetched.')

    all_comments_text = '\n--comment-end--\n'.join(all_comments)
    return all_comments_text


# create a list of include/exclude patterns from a list of name strings
def compile_patterns(names):
    return [re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE) for name in names]


# get patterns list and run findall to count frequency, return final count
def get_player_count(player_data, text):
    include_patterns = compile_patterns(player_data['Include'])
    exclude_patterns = compile_patterns(player_data['Exclude'])

    include_count = sum(len(re.findall(pattern, text)) for pattern in include_patterns)
    exclude_count = sum(len(re.findall(pattern, text)) for pattern in exclude_patterns)

    logging.info(f'{player_data["Name"]}: include count - {include_count} exclude count - {exclude_count}')
    return include_count - exclude_count


# get today's date in MMMDD format
def get_date():
    now = datetime.now()
    return now.strftime('%b%d')


# insert count data into csv
def insert_to_csv(count_data, date):
    logging.info(f'csv header - {date}')

    df = pd.read_csv(CSV_FILE)
    df[date] = count_data
    df.to_csv(CSV_FILE, index=False)
    logging.info(f'Inserted data in CSV file - {CSV_FILE}')


# create post in the subreddit with image and add body text
def create_post(img, sub):
    title = 'Daily Player Trends'
    body = '''
Hello,
I’m a bot that tracks the top 5 most mentioned football players in this subreddit every 24 hours. Each day, I’ll post a line chart showing the trends over the past few days.

How you can help:

- Share feedback and suggestions in the comments.
- Report any issues you notice.

Your input helps improve this bot. Thanks for being part of the community!
'''

    submission = sub.submit_image(title, img)
    submission.edit(body)
    logging.info(f'Post created in {sub.display_name} subreddit.')


# Execution
reddit_instance = create_reddit_instance()
logging.info('create_reddit_instance function completed.')
logging.info('Reddit Initialized.')

reddevils_sub = get_subreddit(SUBREDDIT, reddit_instance)
logging.info('get_subreddit function completed.')

text_data = get_all_comments(reddevils_sub)
logging.info('get_all_comments function completed.')

team_final_count = []
for player in team_data:
    final_count = get_player_count(player, text_data)
    team_final_count.append(final_count)
logging.info('get_player_count function calls completed.')

today = get_date()
logging.info('get_date function completed.')
insert_to_csv(team_final_count, today)
logging.info('insert_to_csv function completed.')

image = chart.create_chart(today, CSV_FILE)
logging.info('create_chart function completed.')
logging.info(f'Chart image - {image} saved.')

test_sub = get_subreddit(TEST_SUB, reddit_instance)
create_post(image, test_sub)
logging.info('create_post function completed.')
logging.info('Execution finished.\nProgram Ends.')
