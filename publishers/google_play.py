import os
import time
import urlparse
import dryscrape


class GooglePlay:
  def __init__(self, username, password, debug_dir=None):
    self.username = username
    self.password = password
    self.debug_dir = debug_dir

    self.session = dryscrape.Session()

    if self.debug_dir:
      if not os.path.exists(self.debug_dir):
        os.mkdir(self.debug_dir)

  def publish(self, appdf):
    self.open_console()
    self.login()
    
    assert self.is_logined()

    if self.is_app_listed(appdf):
      self.open_app(appdf)
    else:
      self.create_app(appdf)

    assert self.is_app_opened(appdf)
    assert self.is_store_listing_opened()

    self.fill_store_listing(appdf)

  def open_console(self):
    self.session.visit("https://play.google.com/apps/publish/v2/")
    self._screenshot("open_console-opened.png")

  def login(self):
    login_url = "https://accounts.google.com/ServiceLogin"

    if self.session.url().startswith(login_url):
      email_field = self.session.at_css("#Email")
      password_field = self.session.at_css("#Passwd")

      email_field.set(self.username)
      password_field.set(self.password)

      self._screenshot("login-filled.png")

      email_field.form().submit()

      time.sleep(3)

      self._screenshot("login-submited.png")

  def is_logined(self):
    url = urlparse.urlparse(self.session.url())
    qs = urlparse.parse_qs(url.query)
    return "dev_acc" in qs

  def is_app_listed(self, appdf):
    xpath = "//p[@data-column='TITLE']/span[contains(text(), '{}')]"
    xpath = xpath.format(appdf.application.description.texts.title)
    return bool(self.session.at_xpath(xpath))

  def open_app(self, appdf):
    xpath = "//p[@data-column='TITLE']/span[contains(text(), '{}')]"
    xpath = xpath.format(appdf.application.description.texts.title)
    self.session.at_xpath(xpath).click()

    time.sleep(3)

    self._screenshot("open_app-opened.png")

  def create_app(self, appdf):
    xpath = "//*[normalize-space(text()) = 'Add new application']"
    self.session.at_xpath(xpath).click()

    self._screenshot("create_app-popup.png")

    title = appdf.application.description.texts.title
    self.session.at_css("div.popupContent input").set(title)

    self._screenshot("create_app-filled.png")

    xpath = "//*[normalize-space(text()) = 'Prepare Store Listing']"
    self.session.at_xpath(xpath).click()

    time.sleep(3)

    self._screenshot("create_app-created.png")

  def is_app_opened(self, appdf):
    xpath = "//h2/span[contains(text(), '{}')]"
    xpath = xpath.format(appdf.application.description.texts.title)
    return bool(self.session.at_xpath(xpath))

  def is_store_listing_opened(self):
    xpath = "//h3[contains(text(), 'Store Listing')]"
    return bool(self.session.at_xpath(xpath))

  def fill_store_listing(self, appdf):
    inputs = self.session.css("fieldset input")
    assert len(inputs) == 7

    textareas = self.session.css("fieldset textarea")
    assert len(textareas) == 3

    selects = self.session.css("fieldset select")
    assert len(selects) == 3

    def fill(elements, values):
      for i, value in enumerate(values):
        if value:
          element = elements[i]
          element.set(value)

    fill(inputs, [
      appdf.application.description.texts.title,
      "http://www.youtube.com/watch?v={}".format(appdf.application.description.videos["youtube-video"]),
      appdf.application["customer-support"].website,
      appdf.application["customer-support"].email,
      appdf.application["customer-support"].phone,
      appdf.application.description.texts["privacy-policy"]
    ])

    fill(textareas, [
      appdf.application.description.texts["full-description"].text.encode("utf-8"),
      appdf.application.description.texts["short-description"],
      appdf.application.description.texts["recent-changes"]
    ])

    rating = {
      3: "SUITABLE_FOR_ALL",
      6: "PRE_TEEN",
      10: "TEEN",
      13: "TEEN",
      17: "MATURE",
      18: "MATURE"
    }[appdf.application["content-description"]["content-rating"]]

    fill(selects, [
      appdf.application.categorization.type.text.upper(),
      appdf.application.categorization.category.text.upper(), # TODO: doesn't work
      rating
    ])

    xpath = "//*[normalize-space(text()) = 'Save']"
    self.session.at_xpath(xpath).click()

    xpath = "//*[normalize-space(text()) = 'Saved']"
    self.session.at_xpath(xpath, timeout=5)

    self._screenshot("fill_store_listing-saved.png")

  def _screenshot(self, name):
    if self.debug_dir:
      file_name = "{}-{}".format(time.time(), name)
      self.session.render(os.path.join(self.debug_dir, file_name))
