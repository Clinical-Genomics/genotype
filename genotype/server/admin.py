# -*- coding: utf-8 -*-
from flask import current_app
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from flask import flash, redirect, request, session, url_for
from flask_login import (LoginManager, login_user, login_required, logout_user,
                         AnonymousUserMixin)
from path import Path
import ruamel.yaml


class AnonymousUser(AnonymousUserMixin):

    def __init__(self):
        self.name = 'Paul T. Anderson'
        self.email = 'pt@anderson.com'

    @property
    def is_authenticated(self):
        if current_app.config.get('LOGIN_DISABLED'):
            return True
        else:
            return False


class UserManagement(object):

    """Provide usermanagement for a Flask app.
    ENV variables:
    GOOGLE_OAUTH_CLIENT_ID
    GOOGLE_OAUTH_CLIENT_SECRET
    USER_DATABASE_PATH
    """

    def __init__(self, manager, User):
        super(UserManagement, self).__init__()
        self.User = User
        self.manager = manager
        self.login_manager = None
        self.blueprint = None
        self.setup()

    def init_app(self, app):
        app.register_blueprint(self.blueprint, url_prefix='/login')

        @app.route('/login')
        def login():
            """Redirect to the Google login page."""
            # store potential next param URL in the session
            if 'next' in request.args:
                session['next_url'] = request.args.get('next')
            return redirect(url_for('google.login'))

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('You have logged out', 'info')
            return redirect(url_for('index'))

        self.login_manager.init_app(app)

    def setup(self):
        self.blueprint = make_google_blueprint(scope=['profile', 'email'])

        # setup login manager
        self.login_manager = LoginManager()
        self.login_manager.login_view = 'login'
        self.login_manager.anonymous_user = AnonymousUser

        @self.login_manager.user_loader
        def load_user(user_id):
            return self.User.query.get(int(user_id))

        @oauth_authorized.connect_via(self.blueprint)
        def google_loggedin(blueprint, token, this=self):
            """Create/login local user on successful OAuth login."""
            if not token:
                flash("Failed to log in with {}".format(blueprint.name), 'danger')
                return redirect(url_for('index'))

            # figure out who the user is
            resp = blueprint.session.get('/oauth2/v1/userinfo?alt=json')

            if resp.ok:
                userinfo = resp.json()

                # check if the user is whitelisted
                email = userinfo['email']
                user_obj = this.User.query.filter_by(email=email).first()
                if user_obj is None:
                    flash("email not whitelisted: {}".format(email), 'danger')
                    return redirect(url_for('index'))

                if user_obj:
                    user_obj.name = userinfo['name']
                    user_obj.avatar = userinfo['picture']
                    user_obj.google_id = userinfo['id']
                else:
                    user_obj = this.User(google_id=userinfo['id'], name=userinfo['name'],
                                         avatar=userinfo['picture'], email=email)
                    this.manager.add(user_obj)

                this.manager.commit()
                login_user(user_obj)
                flash('Successfully signed in with Google', 'success')
            else:
                message = "Failed to fetch user info from {}".format(blueprint.name)
                flash(message, 'danger')

            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('index'))


class UserAdmin(object):

    """docstring for UserAdmin"""

    def __init__(self, database_path=None):
        super(UserAdmin, self).__init__()
        self.database_path = Path(database_path) if database_path else None

    def init_app(self, app):
        """Initialize in Flask app context."""
        self.database_path = Path(app.config['USER_DATABASE_PATH'])

    def confirm(self, email):
        """Confirm that a user has been whitelisted."""
        # read in the file on every request
        with self.database_path.open('r') as in_handle:
            whitelisted_emails = ruamel.yaml.safe_load(in_handle)['whitelist']
        return email in whitelisted_emails
