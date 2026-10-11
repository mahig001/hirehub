"""
Context processors for the core app.
"""


def platform_stats(request):
    """
    Add platform-wide statistics to the template context.
    These will be computed later when we have the models.
    """
    return {
        'platform_name': 'HireHub',
        'platform_tagline': 'Find Your Dream Job',
    }
