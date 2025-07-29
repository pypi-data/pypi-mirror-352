import cv2
import datetime
import json
import requests
import os
import yaml
from aixblock_converter.converter import Converter
from PIL import Image
import io
import uuid

HOSTNAME = os.environ.get("HOSTNAME", "https://app.aixblock.io")


def is_skipped(completion):
    if len(completion['annotations']) != 1:
        return False
    completion = completion['annotations'][0]
    return completion.get('skipped', False) or completion.get('was_cancelled', False)

class CustomConverter(Converter):

    def __get_annotation__(self, image, polygon):

        def flatten(l):
            # flatten list of dictionaries. Take dict['x'] value first, then dict['y'] value.
            flat = []
            for i in l:
                if isinstance(i, dict):
                    flat.append(i['x'])
                    flat.append(i['y'])
                else:
                    flat.extend(i)
            return flat

        points = polygon['points']
        segmentation = [flatten(points)]
        #     Split the polygon points into x and y coordinate lists:
        x_coords = segmentation[0][0::2]
        y_coords = segmentation[0][1::2]
        min_x, max_x = min(x_coords, default=0), max(x_coords)
        min_y, max_y = min(y_coords, default=0), max(y_coords)
        bbox = [min_x, min_y, max_x, max_y]

        width = max_x - min_x
        height = max_y - min_y

        area = width * height

        return segmentation, bbox, area

    def convert_to_coco(self, input_data, output_dir, output_image_dir=None, is_dir=True):
        print("custom COCO converter")
        print(f"input_data: {input_data}")
        print(f"output_dir: {output_dir}")
        # super().convert_to_coco(input_data, output_dir, output_image_dir, is_dir)
        image_urls, image_classes, polygons = [], [], []
        project_id = None

        # TODO: add rectanglelabels support

        # read input_data as json to annotations
        with open(input_data, 'r') as f:
            annotations = json.load(f)

        for annotation in annotations:
            if is_skipped(annotation):
                continue
            try:
                if project_id is None:
                    project_id = annotation['project']
                labels = annotation['annotations'][0]['result']
                for p in labels:
                    if p.get('classification'):
                        if p.get('regionType', '') != 'polygon':
                            continue
                        else:
                            polygons.append(p)
                        image_urls.append(annotation['data']['image'])
                        image_classes.append(p['classification'])
                    elif p.get('polygonlabels'):
                        polygons.append(p['value'])
                        image_urls.append(annotation['data']['image'])
                        image_classes.extends(p['polygonlabels'])
            except Exception as e:
                print(e)

        # unique image classes
        image_classes = list(set(image_classes))
        print(f"Labels: {len(polygons)}")
        print(f"Images: {len(image_urls)}")
        print(f"Classes: {len(image_classes)}")

        print(f'Creating dataset with {len(image_urls)} images...')
        data_location = output_dir

        if not os.path.exists(data_location):
            os.makedirs(data_location)

        # date_created in this format "2023-02-07T16:34:15+00:00" (timezone)
        annotation_json = {
            "info": {
                "year": str(datetime.datetime.now().year),
                "version": "1",
                "description": f"Dataset generated from project {project_id}",
                "contributor": "",
                "url": "",
                "date_created": datetime.datetime.now().isoformat()
            },
            "licenses": [
                {
                    "id": 1,
                    "url": "https://creativecommons.org/licenses/by/4.0/",
                    "name": "CC BY 4.0"
                }
            ],
            "categories": [
                {"id": 0, "name": "WowAI", "supercategory": "none"},
            ],
        }

        annotation_json['categories'] += [
            {"id": i+1, "name": image_classes[i],
                "supercategory": "WowAI"}
            for i in range(0, len(image_classes))
        ]

        def image_class_to_index(img_class):
            # given image_class as value of annotation_json['categories'][i]["names"], return index
            for i in range(len(annotation_json['categories'])):
                if annotation_json['categories'][i]["name"] == img_class and annotation_json['categories'][i]["supercategory"] != "none":
                    return i
        
        # create train, val, test directories
        train_location = os.path.join(data_location, "train")
        val_location = os.path.join(data_location, "val")
        if not os.path.exists(train_location):
            os.makedirs(train_location)
        if not os.path.exists(val_location):
            os.makedirs(val_location)

        # download images to train, val directories. 80% train, 20% val. Each directory has images and _annotations.coco.json file contains the images and annotations
        train_image_urls = image_urls[:int(len(image_urls)*0.8)]
        val_image_urls = image_urls[int(len(image_urls)*0.8):]
        train_polygons = polygons[:int(len(polygons)*0.8)]
        val_polygons = polygons[int(len(polygons)*0.8):]

        # create train dataset
        train_annotations_json = annotation_json.copy()
        train_images = []
        for i, image_url in enumerate(train_image_urls):
            try:
                image_path = os.path.join(train_location, f'{i}.jpg')
                # save image
                print(image_url)
                image = requests.get(image_url).content
                img = Image.open(io.BytesIO(image))
                # Convert the RGBA image to RGB
                img = img.convert('RGB')

                # resize image to 224x224 & 320x320 & 720x720
                # img = img.resize((720, 720))

                # save image as jpg
                img.save(image_path, "JPEG", quality=100,
                        optimize=True, progressive=True)
                train_images.append({
                    "id": i,
                    "width": img.size[0],
                    "height": img.size[1],
                    "file_name": f'{i}.jpg',
                    "license": 1,
                    "date_captured": datetime.datetime.now().isoformat()
                })
            except Exception as e:
                print(e)
        train_annotations_json['images'] = train_images

        train_annotations = []
        for i, polygon in enumerate(train_polygons):
            try:
                image_path = os.path.join(train_location, f'{i}.jpg')
                # read image as numpy array
                image = cv2.imread(image_path)
                segmentation, bbox, area = self.__get_annotation__(image, polygon)
                train_annotations.append({
                    "id": i,
                    "image_id": i,
                    "category_id": image_class_to_index(polygon['classification']),
                    "segmentation":  segmentation,
                    "area": area,
                    "bbox": bbox,
                    # "bbox_mode": BoxMode.XYXY_ABS,
                    "iscrowd": 0
                })
            except Exception as e:
                print(e)

        train_annotations_json['annotations'] = train_annotations

        # write train annotations to file _annotations.coco.json inside train directory
        with open(os.path.join(train_location, '_annotations.coco.json'), 'w') as f:
            train_annotations_json = eval(str(train_annotations_json))
            json.dump(train_annotations_json, f)

        # create val dataset
        val_annotations_json = annotation_json.copy()
        val_images = []
        for i, image_url in enumerate(val_image_urls):
            try:
                image_path = os.path.join(val_location, f'{i}.jpg')
                print(image_url)
                image = requests.get(
                    image_url).content
                img = Image.open(io.BytesIO(image))
                # save image as jpg
                img = img.convert('RGB')
                # img = img.resize((720, 720))
                img.save(image_path, "JPEG", quality=100,
                        optimize=True, progressive=True)
                val_images.append({
                    "id": i,
                    "width": img.size[0],
                    "height": img.size[1],
                    "file_name": f'{i}.jpg',
                    "license": 1,
                    "date_captured": datetime.datetime.now().isoformat()
                })
            except Exception as e:
                print(e)
        val_annotations_json['images'] = val_images

        val_annotations = []
        for i, polygon in enumerate(val_polygons):
            try:
                image_path = os.path.join(val_location, f'{i}.jpg')
                # read image as numpy array
                image = cv2.imread(image_path)
                segmentation, bbox, area = self.__get_annotation__(image, polygon)
                val_annotations.append({
                    "id": i,
                    "image_id": i,
                    "category_id": image_class_to_index(polygon['classification']),
                    "segmentation": segmentation,  # [flatten(polygon['points'])],
                    "area": area,
                    "bbox": bbox,
                    # "bbox_mode": BoxMode.XYXY_ABS,
                    "iscrowd": 0
                })
            except Exception as e:
                print(e)

        val_annotations_json['annotations'] = val_annotations

        # write val_annotations to file _annotations.coco.json inside val directory
        with open(os.path.join(val_location, '_annotations.coco.json'), 'w') as f:
            val_annotations_json = eval(str(val_annotations_json))
            json.dump(val_annotations_json, f)

    def convert_to_yolo(self, input_data, output_dir, output_image_dir=None, output_label_dir=None, is_dir=True):
        print("custom YOLO converter")
        print(f"input_data: {input_data}")
        print(f"output_dir: {output_dir}")

        # keep original convert_to_yolo function for users who don't need to customize
        # super().convert_to_yolo(input_data, output_dir, output_image_dir, output_label_dir, is_dir)

        image_urls, boxes, image_classes = [], [], []
        project_id = None
        print(f'Creating dataset with {len(image_urls)} images...')
        data_location = output_dir

        # read input_data json file and assign to completions
        with open(input_data, "r") as f:
            completions = json.load(f)
        
        for completion in completions:
            # print(completion)
            if not project_id:
                project_id = completion['project']
            # if is_skipped(completion):
            #     continue
            if len(completion['annotations'][0]['result']) == 0:
                continue
            image_boxes = completion['annotations'][0]['result']
            for box in image_boxes:
                # print(box)
                if 'classification' in box:
                    boxes.append(box)
                    image_classes.append(
                        box['classification'])
                    image_urls.append(HOSTNAME + completion['data']['image'])
                elif 'rectanglelabels' in box:
                    # convert x, y, width, height to centerX, centerY, width, height with Normalized
                    x = box['x']
                    y = box['y']
                    # bounding box width
                    w = box['width'] - x
                    # bounding box height
                    h = box['height'] - y
                    width = box['width']
                    height = box['height']
                    box['centerX'] = (x + width / 2) / width
                    box['centerY'] = (y + height / 2) / height
                    box['width'] = w / width
                    box['height'] = h / height
                    box['classification'] = box['rectanglelabels'][0]
                    boxes.append(box)
                    image_classes.append(
                        box['rectanglelabels'][0])
                    image_urls.append(HOSTNAME + completion['data']['image'])
                elif 'bounding-box' in box:
                    # convert x, y, width, height to centerX, centerY, width, height with Normalized
                    if 'x' in box:
                        x = box['x']
                    elif 'centerX' in box:
                        x = box['centerX']
                    if 'y' in box:
                        y = box['y']
                    elif 'centerX' in box:
                        y = box['centerY']
                    
                    # bounding box width
                    w = box['width'] - x
                    # bounding box height
                    h = box['height'] - y
                    width = box['width']
                    height = box['height']
                    box['centerX'] = (x + width / 2) / width
                    box['centerY'] = (y + height / 2) / height
                    box['width'] = w / width
                    box['height'] = h / height
                    if 'classification' in box:
                        box['classification'] = box['classification']
                    boxes.append(box)
                    image_classes.append(box['classification'])
                    image_urls.append(HOSTNAME + completion['data']['image'])
                
            print(image_urls)
            print(image_classes)
        # unique classes
        image_classes = list(set(image_classes))
        # split output_dir images and annotations into train and val, test folders
        # read input_data and split into train and val, test
        # create data.yaml file
        data_location = output_dir
        if not os.path.exists(data_location):
            os.makedirs(data_location)
        data_yaml = {
            "train": os.path.join(data_location, "train"),
            "val": os.path.join(data_location, "val"),
            "nc": len(set(image_classes)),
            "names": {
                i: image_class for i, image_class in enumerate(set(image_classes))
            }
        }
        with open(os.path.join(data_location, "data.yaml"), "w") as f:
            yaml.dump(data_yaml, f)
        
        def image_class_to_index(img_class):
            # given image_class as value of data_yaml["names"], return index
            return list(data_yaml["names"].values()).index(img_class)

        # create train, val, test directories
        train_location = os.path.join(data_location, "train")
        val_location = os.path.join(data_location, "val")
        test_location = os.path.join(data_location, "test")
        if not os.path.exists(train_location):
            os.makedirs(train_location)
        if not os.path.exists(val_location):
            os.makedirs(val_location)
        if not os.path.exists(test_location):
            os.makedirs(test_location)
        
        # save images and labels to train, val, test directories
        # example image_box: {'x': 0.10711754445975784, 'y': 15.113011212416097, 'width': 32.32138899423308, 'height': 82.95757938438739, 'rectanglelabels': ['person']}
        # images will save to `images` dir inside train, val, test,
        # labels will save to `labels` dir inside train, val, test
        for i, (image_url, image_box) in enumerate(zip(image_urls, boxes)):
            name_image = uuid.uuid4()
            image_name = f"{name_image}.jpg"
            label_name = f"{name_image}.txt"
            _image_location = os.path.join(
                    train_location, "images")
            if not os.path.exists(os.path.dirname(_image_location)):
                os.makedirs(os.path.dirname(_image_location))
            label_location = os.path.join(
                    val_location, "labels")
            if not os.path.exists(os.path.dirname(label_location)):
                os.makedirs(os.path.dirname(label_location))
            _label_train_location = os.path.join(
                    train_location, "labels")
            if not os.path.exists(os.path.dirname(_label_train_location)):
                os.makedirs(os.path.dirname(_label_train_location))
            image_location = os.path.join(
                    train_location, "images", image_name)
            
            if not os.path.exists(os.path.join(
                            train_location, 'labels')):
                os.makedirs(os.path.join(
                            train_location, 'labels'))
            if not os.path.exists(os.path.join(
                            train_location, 'images')):
                os.makedirs(os.path.join(
                            train_location, 'images'))
                
            if not os.path.exists(os.path.join(
                            val_location, 'labels')):
                os.makedirs(os.path.join(
                            val_location, 'labels'))
            if not os.path.exists(os.path.join(
                            val_location, 'images')):
                os.makedirs(os.path.join(
                            val_location, 'images'))
            # save image
            print(image_url)
            image = requests.get(
                image_url,verify=False).content
            img = Image.open(io.BytesIO(image))
            # Convert the RGBA image to RGB
            img = img.convert('RGB')

            # resize image to 224x224 & 320x320 & 720x720
            img = img.resize((720, 720))

            # save image as jpg
            
            if i < 0.8 * len(image_urls):
                img.save(os.path.join(os.path.join(
                        train_location, "images"), image_name), "JPEG", quality=100,
                        optimize=True, progressive=True)
                label_location = os.path.join(
                    train_location, 'labels', label_name)
                # print(label_location)
                with open(label_location, "w+") as f: 
                    f.write(
                        f"{image_class_to_index(image_box['classification'])} {image_box['centerX']} {image_box['centerY']} {image_box['width']} {image_box['height']}")
            elif i < 0.9 * len(image_urls):
                img.save(os.path.join(os.path.join(
                        val_location, "images"), image_name), "JPEG", quality=100,
                        optimize=True, progressive=True)
                _image_location = os.path.join(
                    val_location, "images")
                if not os.path.exists(os.path.dirname(_image_location)):
                    os.makedirs(os.path.dirname(_image_location))
                    
                image_location = os.path.join(
                        val_location, "images")

                _label_location = os.path.join(
                        val_location, "labels")
                if not os.path.exists(os.path.dirname(_label_location)):
                    os.makedirs(os.path.dirname(_label_location))

                _image_location = os.path.join(
                        image_location, "images")
                if not os.path.exists(os.path.dirname(_image_location)):
                    os.makedirs(os.path.dirname(_image_location))
                    
                image_location = os.path.join(
                    val_location, "images", image_name)
                with open(image_location, "wb") as f:
                    f.write(image)

                _label_location = os.path.join(
                        val_location, "labels")
                if not os.path.exists(os.path.dirname(_label_location)):
                    os.makedirs(os.path.dirname(_label_location))
                label_location = os.path.join(
                    val_location, 'labels', label_name)
                # save label
                print(label_location)
                with open(label_location, "w+") as f:
                    f.write(
                        f"{image_class_to_index(image_box['classification'])} {image_box['centerX']} {image_box['centerY']} {image_box['width']} {image_box['height']}")
            else:
                if not os.path.exists(os.path.join(
                        test_location, "images")):
                    os.makedirs(os.path.join(
                        test_location, "images"))
                img.save(os.path.join(
                    test_location, 'images', image_name), "JPEG", quality=100,
                     optimize=True, progressive=True)
            
            
            
           
            

            