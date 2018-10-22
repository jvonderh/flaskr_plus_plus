import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Unbelieveable. No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            category='yeah',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'yeah' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_delete(self):
        rv = self.app.get('/delete')
        vr = self.app.get('/add', data=dict(
            title='<hello>',
            category='yeah',
            text='<strong>HTML</strong> allowed here'
        ))
        assert b'No entries here so far' not in vr.data
        assert b'&lt;Hello&gt;' not in rv.data
        assert b'yeah' not in rv.data
        assert b'<strong>HTML</strong> allowed here' not in rv.data

    def test_filter(self):
        rv = self.app.get('/add', data=dict(
            title='<hello>',
            category='yeah',
            text='yeah'
        ))
        vr = self.app.get('filter', data=dict(
            filter='yeah'
        ))
        assert b'No entries here so far' not in vr.data
        assert b'yeah' in rv.data


if __name__ == '__main__':
    unittest.main()