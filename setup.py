"""
Flask-Shopify
-------------

"""
from setuptools import setup


setup(
    name='Flask-Shopify',
    version='0.1',
    url='http://example.com/flask-sqlite3/',
    license='BSD',
    author='Fulfil.IO Inc.',
    author_email='hello@fulfil.io',
    description='Shopify Flask',
    long_description=__doc__,
    py_modules=['flask_shopify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'ShopifyApi',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
