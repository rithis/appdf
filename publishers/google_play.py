import os
import urlparse
import mechanize


class GooglePlay:
  COOKIES_PATH = os.path.expanduser("~/.appdf-publisher-cookies.txt")

  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.cookies = mechanize.LWPCookieJar()
    self.browser = mechanize.Browser()
    self.browser.set_cookiejar(self.cookies)
    self.browser.set_handle_referer(True)
    self.browser.set_handle_robots(False)

    user_agent = ["Mozilla/5.0",
                  "(Macintosh; Intel Mac OS X 10_8_3)",
                  "AppleWebKit/537.22",
                  "(KHTML, like Gecko)",
                  "Chrome/25.0.1364.172",
                  "Safari/537.22"]

    self.browser.addheaders = [('User-agent', " ".join(user_agent))]

  def publish(self, appdf):
    self.read_session()
    self.open_console()
    self.login()
    assert self.is_logined()
    self.save_session()

  def open_console(self):
    self.browser.open("https://play.google.com/apps/publish/v2/")

  def login(self):
    def form_predicate(form):
      return form.action == "https://accounts.google.com/ServiceLoginAuth"

    try:
      self.browser.select_form(predicate=form_predicate)
      self.browser.form.find_control("Email").readonly = False
      self.browser.form["Email"] = self.username
      self.browser.form["Passwd"] = self.password
      self.browser.submit()
    except mechanize._mechanize.FormNotFoundError:
      pass

  def is_logined(self):
    url = urlparse.urlparse(self.browser.geturl())
    qs = urlparse.parse_qs(url.query)
    return "dev_acc" in qs

  def read_session(self):
    if os.path.isfile(GooglePlay.COOKIES_PATH):
      self.cookies.load(GooglePlay.COOKIES_PATH)

  def save_session(self):
    self.cookies.save(GooglePlay.COOKIES_PATH)
