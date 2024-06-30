from utils.validators import (
    user_has_role, 
    user_is_guild_admin, 
    is_dev
)


def is_dev_or_admin_privs(func):
    def wrapper(instance, *args, **kwargs):
        if is_dev(instance.message) or user_has_role(
            instance.admin_role, instance.message
        ):
            return func(instance, *args, **kwargs)
        else:
            raise PermissionError(instance.admin_role)

    return wrapper


def is_dev_or_user_or_admin_privs(func):
    def wrapper(instance, *args, **kwargs):
        if (
            is_dev(instance.message)
            or user_has_role(instance.admin_role, instance.message)
            or user_has_role(instance.user_role, instance.message)
        ):
            return func(instance, *args, **kwargs)
        else:
            raise PermissionError(instance.admin_role + ", " + instance.user_role)

    return wrapper


def is_dev_or_guild_admin(func):
    def wrapper(instance, *args, **kwargs):
        if is_dev(instance.message) or user_is_guild_admin(instance.message):
            return func(instance, *args, **kwargs)
        else:
            raise PermissionError("Admin")

    return wrapper


def is_dev_or_anvil_or_admin_privs(func):
    def wrapper(instance, *args, **kwargs):
        if (
            is_dev(instance.message)
            or user_has_role(instance.admin_role, instance.message)
            or user_has_role(instance.anvil_role, instance.message)
        ):
            return func(instance, *args, **kwargs)
        else:
            raise PermissionError(instance.admin_role + ", " + instance.anvil_role)

    return wrapper
