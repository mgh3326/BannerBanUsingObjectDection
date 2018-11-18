# Import packages
import json
from time import sleep

import telepot
from metadata.jpg_metadata import JPGImageMetaData
from mymongo.mymongo import DBConnect
import json


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if msg['text'] == '/start':  # 시작
            bot.sendMessage(
                chat_id,
                text='처음 오셨군요\n파일 보내기로 원본 이미지를 보내주시면 metadata를 통해서 위치정보 또한 보낼수 있습니다.')
        else:
            bot.sendMessage(
                chat_id,
                text='처음 오셨군요\n파일 보내기로 원본 이미지를 보내주시면 metadata를 통해서 위치정보 또한 보낼수 있습니다.')
            # 가입
    elif content_type == 'photo':
        file_path = './' + str(chat_id) + '.png'

        bot.download_file(msg['photo'][-1]['file_id'], file_path)

        temp = db.put_image(file_path, chat_id)
        if temp == 0:
            bot.sendMessage(chat_id,
                            text="정상적으로 메타 데이터 까지 보내졌습니다.")
        elif temp == 1:
            bot.sendMessage(chat_id,
                            text="위치 정보가 사진에서 찾지 못했습니다.\n위치 정보를 보내주세요")
        elif temp == 2:
            bot.sendMessage(chat_id,
                            text="이전의 사진의 위치 정보를 보내주세요")

        # PATH_TO_IMAGE = os.path.join(CWD_PATH,_image)

    elif content_type == 'location':
        latitude = msg['location']['latitude']
        longitude = msg['location']['longitude']
        temp = db.put_local(msg, chat_id)
        if temp == 0:
            bot.sendMessage(
                chat_id,
                text='이전의 이미지의 위도 경도를 업데이트 하였습니다.\nlatitude : ' + str(latitude) + '\nlongitude : ' + str(longitude))
        elif temp == 1:
            bot.sendMessage(
                chat_id,
                text='위치 정보를 대기중인 이미지가 없습니다. 이미지를 먼저 보내주세요')

    elif content_type == 'document':
        if msg['document']['mime_type'] == "image/jpeg" or "image/png":
            file_path = './' + str(chat_id) + '.jpg'
            bot.download_file(msg['document']['file_id'], file_path)
            temp = db.put_image(file_path, chat_id)
            if temp == 0:
                bot.sendMessage(chat_id,
                                text="정상적으로 메타 데이터 까지 보내졌습니다.")
            elif temp == 1:
                bot.sendMessage(chat_id,
                                text="위치 정보가 사진에서 찾지 못했습니다.\n위치 정보를 보내주세요")
            elif temp == 2:
                bot.sendMessage(chat_id,
                                text="이전의 사진의 위치 정보를 보내주세요")
        # elif msg['document']['mime_type'] == "image/png":
        #     bot.sendMessage(chat_id, text='png를 보내셨네요')
        else:
            bot.sendMessage(chat_id, text='현재 JPEG 이미지와 PNG 이미지만 지원하고 있습니다.')
    else:

        bot.sendMessage(
            chat_id, text='사진을 보내서 제보해주세요\n이미지를 보냈는데 위치 정보가 없다면 위치 정보를 보낼때까지 lock이 걸립니다.')


if __name__ == "__main__":
    print("Start")
    with open('./config/secret.json') as f:
        data = json.load(f)
    db = DBConnect(data["mongodb"])
    print("DB Connect OK")
    bot = telepot.Bot(data["telepot_key"])
    bot.message_loop(handle)
    print('Listening ...')

    while 1:
        # sleep(randint(10, 20))
        sleep(10)
