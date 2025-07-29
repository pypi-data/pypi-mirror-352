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


class ProjectLabels:
    def __init__(self, project_id):
        self.project_id = project_id

    def add_label(self, label_type, name, label, color=None):
        with transaction.atomic():
            project = Project.objects.select_for_update().filter(pk=self.project_id).first()
            root = etree.fromstring(project.label_config)
            label_type = label_type.upper()
            parents = root.xpath(
                "//*[re:test(name(), '^" + label_type + "$', 'i')][@name='" + name + "']",
                namespaces={'re': "http://exslt.org/regular-expressions"},
            )

            if len(parents) == 0:
                return None

            if color is None:
                color = get_random_color()

            parent = parents[0]
            labels = label.split(",")
            added_labels = list([])

            for lbl in labels:
                is_existed = False
                existing_labels = root.xpath(
                    "//*[re:test(name(), '^" + label_type + "$', 'i')][@name='" + name + "']/*[re:test(name(), '(label|choice)', 'i')]",
                    namespaces={'re': "http://exslt.org/regular-expressions"},
                )

                for existing_label in existing_labels:
                    if existing_label.attrib["value"].lower().strip() == lbl.lower().strip():
                        is_existed = True
                        break

                if is_existed:
                    break

                if label_type.lower() == 'choices':
                    new_label = etree.Element("Choice", value=lbl.strip(), background=color)
                else:
                    new_label = etree.Element("Label", value=lbl.strip(), background=color)

                parent.insert(0, new_label)
                added_labels.append({
                    "label": lbl.strip(),
                    "color": new_label.attrib["background"],
                    "type": label_type,
                    "name": name,
                })

            if len(added_labels) > 0:
                project.label_config = etree.tostring(root).decode()
                project.save()

                publish_message(
                    channel=f"project/{self.project_id}",
                    data={
                        "label_config": project.label_config,
                        "added_labels": added_labels,
                    },
                )

            return project.label_config

    def remove_label(self, label_type, name, label):
        with transaction.atomic():
            project = Project.objects.select_for_update().filter(pk=self.project_id).first()
            root = etree.fromstring(project.label_config)
            existing_labels = root.xpath(
                "//*[re:test(name(), '^" + label_type + "$', 'i')][@name='" + name + "']/*[re:test(name(), '^(label|choice)$', 'i')]",
                namespaces={'re': "http://exslt.org/regular-expressions"},
            )
            label = label.strip().lower()
            is_found = False

            for existing_label in existing_labels:
                if existing_label.attrib["value"].strip().lower() == label:
                    existing_label.getparent().remove(existing_label)
                    is_found = True

            if is_found:
                project.label_config = etree.tostring(root).decode()
                project.save()

                publish_message(
                    channel=f"project/{self.project_id}",
                    data={
                        "label_config": project.label_config,
                        "deleted_label": {"label": label, "type": label_type, "name": name},
                    },
                )

            return project.label_config
