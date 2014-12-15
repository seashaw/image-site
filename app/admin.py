"""
File: admin.py
Authors: 
    2014-12-12 - C.Shaw <shaw.colin@gmail.com>
Description:
    Administrative views.
"""

from flask.ext.principal import Permission, RoleNeed
from flask.ext.admin import expose, BaseView, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

class HomeView(AdminIndexView):
    """
    Index view route for administration.
    """
    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class UsersView(ModelView):
    """
    Admin view for user management.
    """
    
    # Display primary key column.
    column_display_pk = True

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class RolesView(ModelView):
    """
    Admin view for role management.
    """
    
    # Display primary key column.
    column_display_pk = True

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class PostsView(ModelView):
    """
    Admin view for post management.
    """
    
    # Display primary key column.
    column_display_pk = True

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class PicturesView(ModelView):
    """
    Admin view for post management.
    """
    
    # Display primary key column.
    column_display_pk = True

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()

class FileView(FileAdmin):
    """
    Manage uploaded files and directories.
    """

    def is_accessible(self):
        """
        Restrict access to authenticated users.
        """
        admin_permission = Permission(RoleNeed('Administrator'))
        return admin_permission.can()
