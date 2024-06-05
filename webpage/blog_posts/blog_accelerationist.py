import blog_posts.base
_ = base._

class PostAccelerationist(base.BaseBlog_):
    Blog_post_id = "asd"
    Category_id = ""
    published_date = None
    file_path = "../templates/posts/accelorationism.html"

    def showBlog():
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()