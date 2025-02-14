from . import users

get_current_user = users.fastapi_users_obj.current_user()
get_current_active_user = users.fastapi_users_obj.current_user(active=True)
get_current_active_verified_user = users.fastapi_users_obj.current_user(active=True, verified=True)

get_current_user_optional = users.fastapi_users_obj.current_user(optional=True)
get_current_active_user_optional = users.fastapi_users_obj.current_user(active=True, optional=True)
get_current_active_verified_user_optional = users.fastapi_users_obj.current_user(active=True, verified=True, optional=True)
