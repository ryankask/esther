import datetime

import pytz

from esther import filters
from esther.tests.helpers import EstherTestCase


class FilterTests(EstherTestCase):
    def test_localize_datetime(self):
        dt = datetime.datetime(2010, 5, 3, 14, 54, 21, tzinfo=pytz.utc)
        naive_dt = datetime.datetime(2010, 5, 3, 15, 54, 21)
        local_dt = self.app.config['TIME_ZONE'].localize(naive_dt)
        self.assertEqual(filters.localize_datetime(dt), local_dt)

    def test_localize_datetime_with_naive_datetime(self):
        dt = datetime.datetime(2010, 5, 3, 14, 54, 21)
        self.assertEqual(filters.localize_datetime(dt), dt)

    def test_format_datetime(self):
        dt = datetime.datetime(2010, 5, 3, 14, 54, 21, tzinfo=pytz.utc)
        self.assertEqual(filters.format_datetime(dt), '03 May 2010 14:54:21 UTC')

    def test_format_datetime_with_format_string(self):
        dt = datetime.datetime(2010, 5, 3, 14, 54, 21, tzinfo=pytz.utc)
        self.assertEqual(filters.format_datetime(dt, '%B %Y %Z'), 'May 2010 UTC')

    def test_format_date(self):
        d = datetime.date(2010, 5, 3)
        self.assertEqual(filters.format_date(d), '03 May 2010')

    def test_format_date_with_format_string(self):
        d = datetime.date(2010, 5, 3)
        self.assertEqual(filters.format_date(d, '%Y'), '2010')

    def test_markdown(self):
        text = '# Test Title'
        self.assertEqual(filters.markdown(text), '<h1>Test Title</h1>')
