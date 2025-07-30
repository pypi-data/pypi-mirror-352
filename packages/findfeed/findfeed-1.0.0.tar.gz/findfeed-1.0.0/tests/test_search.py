'''Minimal test of search functionality.'''

import unittest
from findfeed import search


class TestSearch(unittest.TestCase):
    '''Tests search function'''

    def test_search(self):
        '''Tests search function against a known URL'''

        feeds = search('hackernews.com')
        self.assertTrue(isinstance(feeds, list))

        url = str(feeds[0].url)
        self.assertEqual(url, 'https://news.ycombinator.com/rss')
