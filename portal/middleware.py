class SuperuserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                request.session.set_expiry(86400 * 365)
            else:
                request.session.set_expiry(0)
        return self.get_response(request)
