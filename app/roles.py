'''
File: roles.py
Authors: 
    2015-03-09 by C. Shaw <shaw.colin@gmail.com>
Description: 
    Settings and initialization for role based access control using principal.
'''
from collections import namedtuple
from functools import partial
from flask.ext.principal import Principal, identity_loaded, Permission, \
        RoleNeed, UserNeed
from flask.ext.login import current_user
from . import app, lm
from .model import Role

# Principal object initialization.
principal = Principal(app)

"""
Methods to retrieve roles from database.
"""
def adminRole():
    """
    Returns administrator role from database.
    """
    return Role.query.get(1)

def activeRole():
    """
    Returns active role from database.
    """
    return Role.query.get(2)

def verifiedRole():
    """
    Returns verified role from database.
    """
    return Role.query.get(3)

"""
User permission definitions.
"""
admin_permission = Permission(RoleNeed("Administrator"))
active_permission = Permission(RoleNeed("Active"))
verified_permission = Permission(RoleNeed("Verified"))

# Need and permission for editing user posts.
BlogPostNeed = namedtuple('blog_post', ['method', 'value'])
EditBlogPostNeed = partial(BlogPostNeed, 'edit')

class EditBlogPostPermission(Permission):
    """
    Permission definition for editing blog posts.
    """
    def __init__(self, post_id):
        need = EditBlogPostNeed(str(post_id))
        super(EditBlogPostPermission, self).__init__(need)

@identity_loaded.connect_via(app)
def onIdentityLoaded(sender, identity):
    """
    Connects to the identity-loaded signal to add additional information to
    the Identity instance, like user roles.
    """
    # Set the identity user object.
    identity.user = current_user

    # Add UserNeed to the identity.
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(str(current_user.id)))

    # Update identity with list of roles that User provides.
    # Refers to relationship 'roles' from User model.
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Update identity with list of posts that user authored.
    # Refers to relationship 'posts' from User model.
    if hasattr(current_user, 'posts'):
        for post in current_user.posts:
            identity.provides.add(EditBlogPostNeed(str(post.id)))
