import telepot
import os
import cv2
import analyzeImage

token_api = os.getenv('TOKEN_TELEGRAM')

def toReceive(message):
    _id = message['from']['id']
    if 'text' in message:
        text = message['text']

    try:
        if 'photo' in message:
            tele.sendMessage(_id, "Okay, eu irei analisar a imagem. Isso pode levar um tempo...")
            image_analyzed = analyzeImage.analyze_from_telegram(token_api, message, tele)
            
            tele.sendPhoto(_id, open(image_analyzed, 'rb'))
            tele.sendMessage(_id, "Desculpa a demora, espero que eu tenha acertado.")
        elif 'Oi' in text or 'Olá' in text or 'start' in text:
            tele.sendMessage(_id, "Olá, eu sou o LocaBot.\nEu tento identificar objetos em fotos que você me manda.\nManda uma aí pra me testar.")
        else:
            tele.sendMessage(_id, "Por favor, envie uma imagem para ser análisada.")
    except Exception as e:
        print('Erro:' + str(e))
        tele.sendMessage(_id, "Desculpa, ocorreu um erro. Tente de novo mais tarde.")

tele = telepot.Bot(token_api)
print("Running...")
tele.message_loop(toReceive)

while True:
  pass
