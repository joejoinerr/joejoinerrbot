from __future__ import annotations

import os
import random
import sys

import dotenv
from loguru import logger
import transformers
import tweepy

dotenv.load_dotenv()


PROMPTS = [
    'What if',
    'Who can',
    'Who will',
    'There is a',
    'If I',
    'I just think',
    'Don\'t tell me',
    'That\'s it I\'m',
    'No I will not',
    'Hmm I wonder',
    'Capitalism will',
    'Bold of you to assume I',
    'Sorry that',
    'Why the fuck',
    'What the fuck',
    'The urge to',
    'Yesterday I',
    'Trust',
    'Can we',
    'Sometimes I think about',
    'My dream',
    'This could be',
    'Who actually',
    'I can\'t believe',
    'It\'s so cool that'
    'When I',
    'When we',
    # '@sagittaurean I think you\'re',
    # '@sagittaurean is the best because'
]


def authorize_twitter() -> tweepy.Client | None:
    try:
        bearer_token = os.environ['TWITTER_BEARER_TOKEN']
        consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        access_token = os.environ['TWITTER_ACCESS_KEY']
        access_token_secret = os.environ['TWITTER_ACCESS_SECRET']
        return tweepy.Client(bearer_token=bearer_token,
                             consumer_key=consumer_key,
                             consumer_secret=consumer_secret,
                             access_token=access_token,
                             access_token_secret=access_token_secret)
    except KeyError:
        logger.critical('Twitter secrets were not found in the environment.')
        sys.exit(1)
    except Exception:
        logger.exception('Unknown error while initializing Tweepy.')
        raise


def build_generator() -> transformers.Pipeline:
    return transformers.pipeline('text-generation',
                                 model='huggingtweets/joejoinerr')


def generate_tweets(generator: transformers.Pipeline,
                    prompt: str,
                    result_count: int = 5) -> list[str]:
    tweets = generator(prompt, num_return_sequences=result_count)
    return [tweet for item in tweets
            if '@' not in (tweet := item['generated_text'])]


@logger.catch()
def main():
    logger.info('Starting bot.')
    logger.info('Setting up Twitter.')
    twitter = authorize_twitter()
    logger.info('Twitter set up complete.')
    logger.info('Building tweet generator.')
    generator = build_generator()
    logger.info('Tweet generator built successfully.')
    logger.info('Generating tweets.')
    tweet_choices = generate_tweets(generator, random.choice(PROMPTS))
    if not tweet_choices:
        logger.error('No valid tweets were generated.')
        sys.exit(1)
    logger.info('Successfully generated {} tweets.', len(tweet_choices))
    logger.info('Attempting to send tweet.')
    try:
        tweet_text = random.choice(tweet_choices)
        twitter.create_tweet(text=tweet_text)
    except tweepy.errors.Forbidden:
        logger.critical('Twitter credentials invalid.')
        sys.exit(1)
    logger.info('Bot tweeted successfully.')
    logger.info('Process complete.')


if __name__ == '__main__':
    main()
