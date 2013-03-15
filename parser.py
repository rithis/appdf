import os
from zipfile import ZipFile
from lxml import etree, objectify
from io import StringIO


def parse(file, validate=False):
    """Parse AppDF file and return structured object.

    >>> appdf = parse("samples/Yandex.Shell/yandex.shell.appdf")
    >>> assert isinstance(appdf, objectify.ObjectifiedElement)
    >>> assert appdf.application.attrib["package"] == "ru.yandex.shell"
    >>> assert appdf.application.description.texts.title == "Yandex.Shell"

    >>> parse("samples/Yandex.Shell/yandex.shell.appdf", validate=True)
    Traceback (most recent call last):
        ...
    lxml.etree.DocumentInvalid: Element 'application': The attribute 'platform' is required but missing., line 7

    >>> parse("404 Not Found")
    Traceback (most recent call last):
        ...
    FileNotFoundError: [Errno 2] No such file or directory: '404 Not Found'

    >>> parse("Makefile")
    Traceback (most recent call last):
        ...
    zipfile.BadZipFile: File is not a zip file
    """
    with ZipFile(file, "r") as archive:
        if archive.testzip():
            raise RuntimeError("AppDF file `{}' is broken".format(file))

        if "description.xml" not in archive.namelist():
            raise RuntimeError("Invalid AppDF file `{}'".format(file))

        current_dir = os.path.dirname(os.path.realpath(__file__))
        xsd_file = os.path.join(current_dir, "appdf-description.xsd")
        schema = etree.XMLSchema(etree.parse(xsd_file))
        xml = archive.read("description.xml")

        # disabled, see https://github.com/onepf/AppDF/issues/71
        if validate:
            schema.assertValid(etree.fromstring(xml))

        return objectify.fromstring(xml)
