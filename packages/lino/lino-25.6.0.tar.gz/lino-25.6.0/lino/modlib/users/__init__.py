# Copyright 2011-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# Docs: https://dev.lino-framework.org/plugins/users.html


from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Users")
    needs_plugins = ["lino.modlib.system"]
    active_sessions_limit = -1

    third_party_authentication = False
    allow_online_registration = False
    verification_code_expires = 5
    user_type_new = "user"
    user_type_verified = "user"
    my_setting_text = _("My settings")
    with_nickname = False
    # partner_model = 'contacts.Person'
    partner_model = "contacts.Partner"
    demo_password = "1234"

    def pre_site_startup(self, site):
        super().pre_site_startup(site)
        # if isinstance(self.partner_model, str):
        #     if not site.is_installed_model_spec(self.partner_model):
        #         self.partner_model = None
        #         return
        self.partner_model = site.models.resolve(self.partner_model)

    # def unused_on_plugins_loaded(self, site):
    #     if self.allow_online_registration:
    #         # If you use gmail smtp to send email.
    #         # See: https://support.google.com/mail/answer/7126229?visit_id=1-636656345878819046-1400238651&rd=1#cantsignin&zippy=%2Ci-cant-sign-in-to-my-email-client
    #         # For this setup you will have to allow less secure app access from
    #         # your google accounts settings: https://myaccount.google.com/lesssecureapps
    #         site.update_settings(
    #             EMAIL_HOST='smtp.gmail.com',
    #             EMAIL_PORT=587,  # For TLS | use 465 for SSL
    #             EMAIL_HOST_USER='username@gmail.com',
    #             EMAIL_HOST_PASSWORD='*********',
    #             EMAIL_USE_TLS=True)

    def on_init(self):
        super().on_init()
        self.site.set_user_model("users.User")
        from lino.core.site import has_socialauth

        if has_socialauth and self.third_party_authentication:
            self.needs_plugins.append("social_django")

    def get_requirements(self, site):
        yield "social-auth-app-django"

    def get_used_libs(self, site):
        if self.third_party_authentication:
            try:
                import social_django

                version = social_django.__version__
            except ImportError:
                version = site.not_found_msg
            name = "social-django"

            yield (name, version, "https://github.com/python-social-auth")

    def setup_config_menu(self, site, user_type, m, ar=None):
        g = site.plugins.system
        m = m.add_menu(g.app_label, g.verbose_name)
        m.add_action("users.AllUsers")

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        g = site.plugins.system
        m = m.add_menu(g.app_label, g.verbose_name)
        m.add_action("users.Authorities")
        m.add_action("users.UserTypes")
        m.add_action("users.UserRoles")
        if self.third_party_authentication:
            m.add_action("users.SocialAuths")

    def setup_site_menu(self, site, user_type, m, ar=None):
        m.add_action("users.Sessions")

    def get_quicklinks(self):
        yield "users.Me"
