import json
import random
from django.db import transaction
from lxml import etree

from plugins.plugin_centrifuge import publish_message
from projects.models import Project


def get_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"#{r:02x}{g:02x}{b:02x}"


class ProjectPiiEntities:
    def __init__(self, project_id):
        self.project_id = project_id

    def add(self, name, entity):
        with transaction.atomic():
            project = Project.objects.select_for_update().filter(pk=self.project_id).first()
            root = etree.fromstring(project.label_config)
            redactors = root.xpath(
                "//*[re:test(name(), '^REDACTOR$', 'i')]",
                namespaces={'re': "http://exslt.org/regular-expressions"},
            )

            if len(redactors) == 0:
                return None

            for redactor in redactors:
                if redactor.attrib["name"] != name:
                    continue

                _tmp = "," + redactor.attrib["pii"] + "," if redactor.attrib["pii"] and len(redactor.attrib["pii"]) > 0 else ""

                if "," + entity + "," not in _tmp:
                    if redactor.attrib["pii"]:
                        redactor.attrib["pii"] = entity + "," + redactor.attrib["pii"]
                    else:
                        redactor.attrib["pii"] = entity

                    project.label_config = etree.tostring(root).decode()
                    project.save()

                publish_message(
                    channel=f"project/{self.project_id}",
                    data={
                        "label_config": project.label_config,
                        "added_pii": {"name": name, "entity": entity},
                    },
                )

                return project.label_config

        return None

    def remove(self, name, entity):
        with transaction.atomic():
            project = Project.objects.select_for_update().filter(pk=self.project_id).first()
            root = etree.fromstring(project.label_config)
            redactors = root.xpath(
                "//*[re:test(name(), '^REDACTOR$', 'i')]",
                namespaces={'re': "http://exslt.org/regular-expressions"},
            )

            if len(redactors) == 0:
                return None

            for redactor in redactors:
                if redactor.attrib["name"] != name:
                    continue

                _tmp = "," + redactor.attrib["pii"] + "," if redactor.attrib["pii"] and len(redactor.attrib["pii"]) > 0 else ""

                if "," + entity + "," in _tmp:
                    redactor.attrib["pii"] = _tmp.replace("," + entity + ",", ",").strip(",")
                    project.label_config = etree.tostring(root).decode()
                    project.save()

                    publish_message(
                        channel=f"project/{self.project_id}",
                        data={
                            "label_config": project.label_config,
                            "deleted_pii": {"name": name, "entity": entity},
                        },
                    )

                    return project.label_config

                break

        return None
