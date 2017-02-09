import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
        
class Post(db.Model):
    title = db.StringProperty(required = True)
    post_text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", post_text = "", error=""):
        #posts = db.GqlQuery("select * from Post order by created desc limit 5")
        page = self.request.get("page")
        post_limit=5
        if page == "": #no value
            page = 0
            post_offset=0
        else: #page exists
            page = int(page)
            post_offset=(page*5)
        posts = get_posts(post_limit, post_offset)
        self.render("front.html", title=title, post_text=post_text, error=error, posts=posts, limit=post_limit, page=page)
        #page and post_limit are passed for navigation
            
    def get(self):
            
        self.render_front()
        
class NewPost(Handler):
    def render_new(self, title="", post_text = "", error=""):
        self.render("newpost.html", title=title, post_text=post_text, error=error)

    
    def get(self):
        self.render_new()
        
    def post(self):
        title = self.request.get("title")
        post_text = self.request.get("post_text")
        
        if title and post_text:
            a = Post(title = title, post_text = post_text)
            a.put()
            key = str(a.key().id())
            redirectstring = "/blog/"+key
            self.redirect(redirectstring)
            
        else:
            error = "You need both a title and text."
            self.render_new(title, post_text, error)
            
class ViewPostHandler(Handler):
    def get(self, id):
        if Post.get_by_id(int(id)):
            post = Post.get_by_id(int(id))
            #self.response.write(post.post_text)
            self.render("singlepost.html", title=post.title, text=post.post_text)
        else:
            error = "No post found with that id"
            #posts = db.GqlQuery("select * from Post order by created desc limit 5")
            post_limit=5
            page = 0
            post_offset=0
            posts = get_posts(post_limit, post_offset)
            self.render("front.html", error=error, posts=posts, limit=post_limit, page=page)
        
def get_posts(limit, offset):
    base_string = "select * from Post order by created desc limit "
    off_string = " offset "
    limit_str = str(limit)
    offset_str = str(offset)
    pass_string = base_string+limit_str+off_string+offset_str 
    return db.GqlQuery(pass_string)
    
app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
