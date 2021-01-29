import io
import os
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import storage



def getLabelsAnnotation(img_path):
    client = vision.ImageAnnotatorClient()
    with io.open(img_path, 'rb') as img_file:
        content = img_file.read()
    
    image = types.Image(content=content)
    
    # solicita detecção da imagem
    response = client.label_detection(image=image)
    labels = response.label_annotations
    return labels
    
def upload_blob(bucket_name, src_file, destination):
 client = storage.Client()
 bucket = client.bucket(bucket_name)
 blob = bucket.blob(destination)
 blob.upload_from_filename(src_file)
 print('####File {} uploaded to {}####'.format(src_file, destination))
