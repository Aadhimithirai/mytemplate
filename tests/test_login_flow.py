"""Backend coverage for the login flow.

The conftest ``testapp`` fixture seeds user@example.com with the password
``safepassword``, so these tests exercise the same credentials a real user
would type on /login.
"""

create_user = True


class TestLoginFlow:

    def test_login_page_shows_the_rebranded_name(self, testapp):
        """The login page renders and carries the MyTemplate branding."""
        rv = testapp.get('/login')

        assert rv.status_code == 200
        body = rv.data.decode()
        assert 'MyTemplate' in body
        assert 'Login to your account' in body

    def test_valid_credentials_reach_the_dashboard(self, testapp):
        """A seeded user can log in and then open their team dashboard.

        /dashboard/ redirects to a team-scoped URL (/dashboard/<team_hashid>),
        so the request follows redirects rather than asserting on the path.
        """
        rv = testapp.post('/login', data={
            'email': 'user@example.com',
            'password': 'safepassword',
        }, follow_redirects=True)

        assert rv.status_code == 200
        assert 'Logged in successfully.' in rv.data.decode()

        dashboard = testapp.get('/dashboard/', follow_redirects=True)

        assert dashboard.status_code == 200
        body = dashboard.data.decode()
        assert 'team Dashboard' in body
        assert 'New Tickets' in body

    def test_wrong_password_is_rejected(self, testapp):
        """A bad password keeps the user on the login page, not the dashboard."""
        rv = testapp.post('/login', data={
            'email': 'user@example.com',
            'password': 'not-the-password',
        }, follow_redirects=True)

        assert rv.status_code == 200
        body = rv.data.decode()
        assert 'Logged in successfully.' not in body
        assert 'team Dashboard' not in body

    def test_dashboard_requires_authentication(self, testapp):
        """An anonymous visitor is redirected away from the dashboard."""
        rv = testapp.get('/dashboard/')

        assert rv.status_code == 302
        assert '/login' in rv.headers['Location']
