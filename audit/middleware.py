from .models import ActivityLog


class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            ActivityLog.objects.create(
                actor=request.user,
                action=f'{request.method} {request.resolver_match.view_name if request.resolver_match else request.path}',
                path=request.path[:255],
                method=request.method,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
            )
        return response

    def get_client_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
