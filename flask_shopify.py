# -*- coding: utf-8 -*-
"""
    flask.ext.shopify
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by Fulfil.IO Inc.
    :license: BSD, see LICENSE for more details.
"""
from functools import wraps

from flask import (
    request, redirect, url_for, _request_ctx_stack, session,
    current_app, abort
)
import shopify


DEFAULT_SHOPIFY_API_VERSION = '2019-04'


def assert_shop(func):
    """
    Ensure that the shop in the session is the same as the shop in a landing
    page where something like an admin link is used.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.shopify_session.url == request.args.get('shop'):
            return func(*args, **kwargs)
        else:
            current_app.shopify.logout()
            if current_app.shopify.login_view:
                return redirect(
                    url_for(
                        current_app.shopify.login_view,
                        shop=request.args.get('shop')
                    )
                )
            else:
                abort(403)
    return wrapper


def shopify_login_required(func):
    """
    Ensure that there is a login token in the session.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        shop_n_token = current_app.shopify.tokengetter_func()
        if not shop_n_token:
            return redirect(url_for(
                current_app.shopify.login_view,
                shop=request.args.get('shop'),
                next=request.url
            ))

        with shopify.Session.temp(*shop_n_token):
            return func(*args, **kwargs)

    return decorated_view


class Shopify(object):
    """
    Shopify flask extension

    Required Flask settings::

        SHOPIFY_SHARED_SECRET
        SHOPIFY_API_KEY

    Configuring::

        ```
        from flask_shopify import Shopify

        app = Flask(__name__)
        shopify = Shopify(app)

        # Set the login view if you plan on using shopify_login_required
        # decorator
        shopify.login_view = 'auth.login'

    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(self.app)
        self.tokengetter_func = self._session_token_getter
        self.tokensetter_func = self._session_token_setter
        self.login_view = None

    def init_app(self, app):
        app.shopify = self
        shopify.Session.setup(
            api_key=app.config['SHOPIFY_API_KEY'],
            secret=app.config['SHOPIFY_SHARED_SECRET']
        )
        app.before_request(self.before_request)
        self.api_version = app.config.get(
            'SHOPIFY_API_VERSION',
            DEFAULT_SHOPIFY_API_VERSION
        )

    def before_request(self):
        """
        Add the shopify_session to the request if possible.
        If there is no token, shopify_session is set to None.
        """
        shop_token = self.tokengetter_func()

        ctx = _request_ctx_stack.top
        if shop_token is not None:
            # should be a valid token
            domain, token = shop_token
            shop_session = shopify.Session(domain, self.api_version, token)
            shopify.ShopifyResource.activate_session(shop_session)
            ctx.request.shopify_session = shop_session
        else:
            # not logged in, no session created
            ctx.request.shopify_session = None

    def install(self, shop_subdomain, scopes=None, redirect_uri=None):
        """Returns a redirect response to the "permission" URL with
        the given shop. This will then prompt the user to install the app
        which will then send them to the welcome view.

        :param url: myshopify.com subdomain.
        :type url: str.
        """
        if scopes is None:
            scopes = self.app.config.get('SHOPIFY_SCOPES', [])
        shop_session = shopify.Session(
            "%s.myshopify.com" % shop_subdomain,
            self.api_version
        )
        permission_url = shop_session.create_permission_url(
            scopes, redirect_uri
        )
        return redirect(permission_url)

    def authenticate(self):
        shop_session = shopify.Session(request.args['shop'], self.api_version)
        token = shop_session.request_token(request.args)
        shopify.ShopifyResource.activate_session(shop_session)
        self.tokensetter_func(request.args['shop'], token)
        return shop_session

    def token_getter(self, f):
        """Registers a function as tokengetter.  The tokengetter has to return
        a tuple of ``(url, token)`` with the user's token and secret.
        If the data is unavailable, the function must return `None`.
        """
        self.tokengetter_func = f
        return f

    def token_setter(self, f):
        """Registers a function as tokensetter.  The tokensetter will be sent
        the shop and the token.
        """
        self.tokensetter_func = f
        return f

    @classmethod
    def _session_token_getter(cls):
        try:
            return session['SHOPIFY_SHOP'], session['SHOPIFY_TOKEN']
        except KeyError:
            return None

    @classmethod
    def _session_token_setter(cls, shop, token):
        session['SHOPIFY_SHOP'] = shop
        session['SHOPIFY_TOKEN'] = token

    def logout(self):
        session.pop('SHOPIFY_SHOP', None)
        session.pop('SHOPIFY_TOKEN', None)
        shopify.ShopifyResource.clear_session()
