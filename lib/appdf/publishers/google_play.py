import os
import re
import time
import json
import httplib
import urlparse
import dryscrape


def fill(elements, values):
    for i, value in enumerate(values):
        if value:
            element = elements[i]
            element.set(value)
            element.eval_script("""
                var event = document.createEvent("HTMLEvents");
                event.initEvent("change", true, true);
                node.dispatchEvent(event);
            """)


class GooglePlay(object):
    def __init__(self, app, username, password, debug_dir=None):
        self.app = app
        self.username = username
        self.password = password
        self.debug_dir = debug_dir

        self.session = dryscrape.Session()

        if self.debug_dir:
            if not os.path.exists(self.debug_dir):
                os.mkdir(self.debug_dir)

    # Publication process
    def publish(self):
        self.open_console()
        self.login()

        assert bool(self.ensure_all_applications_header())

        if self.ensure_application_listed():
            self.open_app()
        else:
            self.create_app()

        assert bool(self.ensure_application_header())
        assert bool(self.ensure_store_listing_header())

        self.fill_store_listing()

    # Checks
    def ensure_all_applications_header(self):
        xpath = "//h2[normalize-space(text()) = 'All applications']"
        return self._ensure(xpath)

    def ensure_application_listed(self):
        xpath = "//p[@data-column='TITLE']/span[contains(text(), '{}')]"
        return self._ensure(xpath.format(self.app.title()))

    def ensure_application_header(self):
        xpath = "//h2/span[contains(text(), '{}')]".format(self.app.title())
        return self._ensure(xpath)

    def ensure_store_listing_header(self):
        return self._ensure("//h3[contains(text(), 'Store Listing')]")

    def ensure_saved_message(self):
        return self._ensure("//*[normalize-space(text()) = 'Saved']")

    def _ensure(self, xpath):
        return self.session.at_xpath(xpath, timeout=5)

    # Actions
    def open_console(self):
        self.session.visit("https://play.google.com/apps/publish/v2/")
        self._debug("open_console", "opened")

    def login(self):
        login_url = "https://accounts.google.com/ServiceLogin"

        if self.session.url().startswith(login_url):
            email_field = self.session.at_css("#Email")
            password_field = self.session.at_css("#Passwd")
            email_field.set(self.username)
            password_field.set(self.password)
            self._debug("login", "filled")

            email_field.form().submit()
            self.ensure_all_applications_header()
            self._debug("login", "submited")

    def open_app(self):
        xpath = "//p[@data-column='TITLE']/span[contains(text(), '{}')]"
        self.session.at_xpath(xpath.format(self.app.title())).click()
        self.ensure_application_header()
        self._debug("open_app", "opened")

    def create_app(self):
        xpath = "//*[normalize-space(text()) = 'Add new application']"
        self.session.at_xpath(xpath).click()
        self._debug("create_app", "popup_opened")

        self.session.at_css("div.popupContent input").set(self.app.title())
        self._debug("create_app", "filled")

        xpath = "//*[normalize-space(text()) = 'Prepare Store Listing']"
        self.session.at_xpath(xpath).click()
        self.ensure_application_header()
        self._debug("create_app", "created")

    def fill_store_listing(self):
        inputs = self.session.css("fieldset input")
        textareas = self.session.css("fieldset textarea")
        selects = self.session.css("fieldset select")

        assert len(inputs) == 7
        assert len(textareas) == 3
        assert len(selects) == 3

        fill(inputs, [
            self.app.title(),
            self.app.video(),
            self.app.website(),
            self.app.email(),
            self.app.phone(),
            self.app.privacy_policy()
        ])

        fill(textareas, [
            self.app.full_description(),
            self.app.short_description(),
            self.app.recent_changes()
        ])

        fill(selects, [
            self.app.type(),
            self.app.category(),
            self.app.rating()
        ])

        file_id = 0

        for filename, file_size, file_content in self.app.screenshots():
            upload_metadata = json.dumps({
                "1": 3,
                "3": 1,
                "6": "tmp.09121899434464261693.1364400600658",
                "7": "09121899434464261693",
                "9": "en-US",
                "13":"AMtNNDHURPNKK_3jT3c4rJBnCBQRYiGkTA:1364885170898"
            })

            body = json.dumps({
                "protocolVersion": "0.8",
                "createSessionRequest": {
                    "fields": [
                        {
                            "external": {
                                "name": "file",
                                "filename": filename,
                                "put": {},
                                "size": file_size
                            }
                        },
                        {
                            "inlined": {
                                "name": "upload_metadata",
                                "content": upload_metadata,
                                "contentType": "text/plain"
                            }
                        }
                    ]
                }
            })

            prog = re.compile("domain=(\.?play)?.google.com;")
            cookies = self.session.cookies()
            cookies = filter(lambda c: prog.search(c), cookies)
            cookies = map(lambda c: c.split(";")[0], cookies)
            cookies = "; ".join(cookies)

            headers = {
                "accept": "*/*",
                "accept-charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
                "accept-encoding": "gzip,deflate,sdch",
                "accept-language": "en-US,en;q=0.8",
                "content-length": len(body),
                "content-type": "application/x-www-form-urlencoded",
                "cookie": cookies,
                "referer": self.session.url(),
                "user-agent": self.session.eval_script("navigator.userAgent")
            }

            connection = httplib.HTTPSConnection("play.google.com")
            connection.request("POST", "/apps/publish/v2/upload", body, headers)
            response = connection.getresponse()
            assert response.status == 200
            connection.close()

            upload_url = response.getheader("location")
            upload_url = upload_url.replace("https://play.google.com", "")
            upload_url += "&file_id={}".format(str(file_id).zfill(3))

            file_id += 1

            headers["content-length"] = file_size
            headers["content-type"] = "application/octet-stream"
            headers["x-http-method-override"] = "PUT"

            connection = httplib.HTTPSConnection("play.google.com")
            connection.request("POST", upload_url, file_content, headers)
            response = connection.getresponse()
            assert response.status == 200
            connection.close()

        self.session.at_xpath("//*[normalize-space(text()) = 'Save']").click()
        self.ensure_saved_message()
        self._debug("fill_store_listing", "saved")

    # Helpers
    def _debug(self, action, state):
        if self.debug_dir:
            file_name = "{}-{}-{}.png".format(time.time(), action, state)
            self.session.render(os.path.join(self.debug_dir, file_name))
