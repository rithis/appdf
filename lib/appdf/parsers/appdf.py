import os
import zipfile
import lxml.etree
import lxml.objectify


def silent(f):
    def decorate(self):
        try:
            return f(self)
        except AttributeError:
            return None

    return decorate


def normalize(f):
    def decorate(self):
        result = f(self)

        if isinstance(result, lxml.objectify.ObjectifiedDataElement):
            return result.text.encode("utf-8")
        else:
            return result

    return decorate


class AppDF(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.archive = None

    def parse(self):
        self.archive = zipfile.ZipFile(self.file_path, "r")

        if self.archive.testzip():
            raise RuntimeError("AppDF file `{}' is broken".format(file))

        if "description.xml" not in self.archive.namelist():
            raise RuntimeError("Invalid AppDF file `{}'".format(file))

        self.xml = self.archive.read("description.xml")
        self.obj = lxml.objectify.fromstring(self.xml)

    def validate(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        xsd_file = os.path.join(current_dir, "..", "..", "..", "spec",
                                "appdf-description.xsd")
        schema = lxml.etree.XMLSchema(lxml.etree.parse(xsd_file))
        schema.assertValid(lxml.etree.fromstring(self.xml))

    @silent
    @normalize
    def title(self):
        return self.obj.application.description.texts.title

    def video(self):
        url = None

        if self.obj.application.description.videos["youtube-video"]:
            video_id = self.obj.application.description.videos["youtube-video"]
            url = "http://www.youtube.com/watch?v={}".format(video_id)

        return url

    @silent
    @normalize
    def website(self):
        return self.obj.application["customer-support"].website

    @silent
    @normalize
    def email(self):
        return self.obj.application["customer-support"].email

    @silent
    @normalize
    def phone(self):
        return self.obj.application["customer-support"].phone

    @silent
    @normalize
    def privacy_policy(self):
        return self.obj.application.description.texts["privacy-policy"]

    @silent
    @normalize
    def full_description(self):
        return self.obj.application.description.texts["full-description"]

    @silent
    @normalize
    def short_description(self):
        return self.obj.application.description.texts["short-description"]

    @silent
    @normalize
    def recent_changes(self):
        return self.obj.application.description.texts["recent-changes"]

    @silent
    @normalize
    def type(self):
        return self.obj.application.categorization.type

    @silent
    @normalize
    def category(self):
        return self.obj.application.categorization.category

    @silent
    @normalize
    def rating(self):
        return self.obj.application["content-description"]["content-rating"]
