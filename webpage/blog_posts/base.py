import gettext
from ..database import *
_ = gettext.gettext
class BaseBlog_:

    Blog_post_id = None
    Category_id = None
    published_date = None
    file_path = None

    def __init__(self, access_key, db:Database):
        pass
    def showBlog():
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def to_db():
        db.insert_blog_post(Blog_post_id,Category_id, published_date)