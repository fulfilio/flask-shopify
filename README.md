## Installation

`pip install flask-shopify`

## Settings/Config

The API Key and shared secret should be set on the config of
the app

```
SHOPIFY_SHARED_SECRET   = Your app's shared secret key with Shopify.
SHOPIFY_API_KEY         = Your app's API key.
```

### Optional

```
SHOPIFY_SCOPES          = The default API scopes to request.
SHOPIFY_API_VERSION     = The specific version of the Shopify API to use.
```

## Example usage

### Setup the app

```
from flask_shopify import Shopify

app = Flask(__name__)
shopify = Shopify(app)
```

or, if you are using the factory pattern

```
from flask_shopify import Shopify

shopify = Shopify()

# ...
# when app is available

shopify.init_app(app)
```

### Using `shopify_login_required` decorator

The decorator allows protecting handles with a shopify session.

Before you can use the decorator, ensure that a login view is
configured. This is where fulfil will redirect the user is there
is no login session yet.

```
# Set the login view if you plan on using shopify_login_required
# decorator
shopify.login_view = 'auth.login'
```

Using decorator

```
from flask_shopify import shopify_login_required

@shopify_login_required
@app.route('/product')
def product():
    product = shopify.Product.find(
        request.args['id']
    )
```

### When using admin links

If you are using admin links, then shopify launches the url
with the shop in the parameters. You can use the `assert_shop`
decorator to ensure that the current shop the user is logged
into is also the shop where the user clicked the admin link.

```
from flask_shopify import shopify_login_required, assert_shop

@shopify_login_required
@assert_shop
@app.route('/product')
def product():
    product = shopify.Product.find(
        request.args['id']
    )
```


### Login, logout and oauth authentication

Built-in helpers achieve all of this.

#### Login

```
@app.route('/login')
def login():
    shop = request.args.get('shop')
    if shop:
        return shopify.install(
            shop,
            ['write_products'],
            url_for('.authenticate', _external=True)
        )
    return render_template('select-shop.html')
```

#### Authenticate after Oauth dance

```
@app.route('/authenticate')
def authenticate():
    shopify_session = shopify.authenticate()
    if shopify_session:
        return redirect(
            session.pop('next_url', url_for('.index'))
        )
    return "Login Failed"
```

#### Logout

```
@app.route('/logout')
def logout():
    shopify.logout()
    return redirect('home')
```
