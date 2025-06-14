from .utils import get_dashboard_stats

def dashboard_stats(request):
    """Add dashboard stats to all templates"""
    if request.user.is_authenticated:
        return {'dashboard_stats': get_dashboard_stats()}
    return {}
