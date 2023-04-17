from index import index_blueprint
from facebook_ad.fb import ads_library_blueprint
from app import app


app.register_blueprint(index_blueprint, url_prefix='/')
app.register_blueprint(ads_library_blueprint, url_prefix='/ads')