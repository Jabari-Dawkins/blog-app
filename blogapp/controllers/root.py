# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from blogapp import model
from blogapp.controllers.secure import SecureController
from blogapp.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController
from datetime import datetime

from blogapp.lib.base import BaseController
from blogapp.controllers.error import ErrorController
from blogapp.model.post import Post

import uuid

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the blog-app application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "blogapp"

    @expose('blogapp.templates.post')
    def _default(self, id=""):
        """Handle the front-page."""
        if id == "":
            redirect('/')
        else:
            post = DBSession.query(Post).filter_by(id=id).one()
        return dict(post=post)

    @expose('blogapp.templates.home')
    def index(self):
        """Show newest three blog posts."""
        newestThree = DBSession.query(Post).order_by(Post.dateCreated)[0:3]
        return dict(newestThree=newestThree)

    @expose('blogapp.templates.edit')
    def new(self):
        """Add New Blog Post"""
        post = Post()
        return dict(post=post)

    @expose('blogapp.templates.edit')
    def edit(self, id=""):
        post = DBSession.query(Post).filter_by(id=id).one()
        return dict(post=post)

    @expose()
    def save(self, title, body, submit, id=""):
        if id == "":
            id = str(uuid.uuid4())
            post = Post(id = id, body = body, title = title, dateCreated = datetime.now())
            DBSession.add(post)
        else:
            post = DBSession.query(Post).filter_by(id=id).one()
            post.dateChanged = datetime.now()
            post.body = body
            post.title = title
        redirect('/' + id)
    
    @expose()
    def delete(self, id):
        post = DBSession.query(Post).filter_by(id=id)
        DBSession.delete(post)
        redirect('/')

    @expose('blogapp.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('blogapp.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('blogapp.templates.data')
    @expose('json')
    def data(self, **kw):
        """
        This method showcases how you can use the same controller
        for a data page and a display page.
        """
        return dict(page='data', params=kw)
    @expose('blogapp.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('blogapp.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('blogapp.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login', params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
