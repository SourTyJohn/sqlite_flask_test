from flask_login import UserMixin, LoginManager
from data.models import User


__all__ = (
    "login_manager"
)


class AuthUser(UserMixin):
    id: str

    def __init__(self, fio):
        self.id = fio

    @classmethod
    def get(cls, idd):
        data = User.get_all(sql_filter=f'fio="{idd}"')[0]
        return AuthUser( data[0] )


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return AuthUser.get( user_id )
