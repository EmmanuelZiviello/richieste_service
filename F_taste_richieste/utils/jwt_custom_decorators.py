from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from redis import ConnectionError

# Here is some custom decorators that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user has
# the right role

def paziente_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except ConnectionError:
                return {"message": "Connection error with Redis"}, 500
            except Exception as e:
                return {"message": "Unauthorized"}, 401
            claims = get_jwt()
            if claims["role"] == 'patient':
                return fn(*args, **kwargs)
            else:
                raise NoAuthorizationException("Patient only")

        return decorator

    return wrapper


def nutrizionista_required():
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                try:
                    verify_jwt_in_request()
                except ConnectionError:
                    return {"message": "Connection error with Redis"}, 500
                except:
                    return {"message": "Unauthorized"}, 401
                claims = get_jwt()
                if claims["role"] == 'dietitian':
                    return fn(*args, **kwargs)
                else:
                    raise NoAuthorizationException("Dietitian only!")

            return decorator

        return wrapper

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except ConnectionError:
                return {"message": "Connection error with Redis"}, 500
            except:
                return {"message": "Unauthorized"}, 401
            claims = get_jwt()
            if claims["role"] == 'admin':
                return fn(*args, **kwargs)
            else:
                raise NoAuthorizationException("Admin only!")

        return decorator

    return wrapper

class NoAuthorizationException(Exception):
    pass
#    def __init__(self, message, errors):            
        # Call the base class constructor with the parameters it needs
    #    super().__init__(message)
            
        # Now for your custom code...
    #    self.errors = errors