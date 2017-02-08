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
        posts = db.GqlQuery("select * from Post order by created desc limit 5")
        self.render("front.html", title=title, post_text=post_text, error=error, posts=posts)
            
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
            self.redirect("/blog")
            
        else:
            error = "We need both a title and text."
            self.render_front(title, post_text, error)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', NewPost)
], debug=True)
