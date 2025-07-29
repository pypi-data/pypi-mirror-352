# def predicate(func):
#     """
#     predicate decorator just marks that method of domain model must be exposed 
#     """
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#     return wrapper

class predicate:
    def __init__(self, function):
        self.function = function
     
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)