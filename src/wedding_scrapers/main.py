#!/usr/bin/env python
from wedding_scrapers.crew import WeddingScrapersCrew

def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'urls': [
            'https://www.larisagancea.com/home',
        ]
    }
    WeddingScrapersCrew().crew().kickoff(inputs=inputs)