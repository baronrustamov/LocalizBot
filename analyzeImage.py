import wget
import cv2
from datetime import datetime
from google.cloud import vision
from google.cloud import translate_v2 as translate

def  analyze_from_telegram(token_api, message, tele):
    downloaded_image = download_from_telegram(token_api, message, tele)
    analyzed_image = localize_objects(downloaded_image)
    return analyzed_image

def download_from_telegram(token_api, message, tele):
    print("Fazendo download de arquivo...")
    file_id = message['photo'][1]['file_id']
    file_path = tele.getFile(file_id)['file_path']
    url_image = "https://api.telegram.org/file/bot{}/{}".format(token_api, file_path) 
    
    image_downloaded_path = "./images/{}.jpg".format(str(datetime.now()))
    wget.download(url_image, image_downloaded_path)
    
    return image_downloaded_path


def localize_objects(path):
    print("Localizando Objetos...")
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    data_objects = []
    image = cv2.imread(path)
    h, w, _ = image.shape

    print('\nNúmero de objetos encontrados: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (Confiança: {})'.format(object_.name, object_.score))        
        coordinates = []        
        for vertex in object_.bounding_poly.normalized_vertices:            
            coordinates.append((vertex.x*w, vertex.y*h))        
        data_objects.append([(coordinates[0][0], coordinates[0][1]),
                            (coordinates[2][0], coordinates[2][1]),
                            (object_.name),(object_.score)])
        
    return draw_objects_and_create_new_image(image, data_objects)


def draw_objects_and_create_new_image(image, data_object):
    print("Desenhando retangulos e rotulando imagens...")
    for data in data_object:
        vertice_top = (int(data[0][0]), int(data[0][1]))
        vertice_bottom = (int(data[1][0]), int(data[1][1]))
        object_name = data[2]
        object_score = data[3]

        cv2.rectangle(image, vertice_top, vertice_bottom, (255, 255, 0), 3)

        x, y = int(data[0][0]), int(data[0][1])

        label = translate_label(object_name)
        precision = round(object_score*100)
        label += " {}%".format(precision)

        cv2.putText(image, label, (x, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 0, 0), 1, lineType=cv2.LINE_AA)
        
    dir_image = 'result.jpg'
    cv2.imwrite(dir_image, image)

    return dir_image

def translate_label(text):
    print("Traduzindo label...")
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='pt-BR')
    return result['translatedText']
