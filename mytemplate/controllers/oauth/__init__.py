from .google import blueprint as google_blueprint

# Re-exported for callers that register the OAuth blueprints.
__all__ = ["google_blueprint"]
