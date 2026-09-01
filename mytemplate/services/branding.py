class Branding:
    def __init__(self):
        self.environment = "prod"
        self.config = {}

    def init_app(self, app):
        self.config  = app.config
        self.environment = app.config.get('ENV', 'prod')

    @property
    def name(self):
        if self.environment == "dev":
            return "MyTemplate (dev)"
        return "MyTemplate"

    @property
    def support_email(self):
        email = self.config.get('support_email', 'help@example.com')
        return email

    @property
    def icon_path(self):
        return "public/mytemplate/mytemplate-logo.svg"

    @property
    def svg_icon(self):
        return "public/mytemplate/mytemplate-icon.svg"

    @property
    def website_domain(self):
        return "mytemplate.com"

    @property
    def legal_name(self):
        return "MyTemplate"

    @property
    def corporate_jurisdiction(self):
        return "United States"

    @property
    def full_logo_path(self):
        # The @2x PNG has the old wordmark baked into its pixels; the SVG
        # renders the name as text, so it picks up the rename correctly.
        return "public/mytemplate/mytemplate-logo.svg"

