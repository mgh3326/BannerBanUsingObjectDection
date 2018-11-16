import pymongo
from PIL import Image
from gridfs import GridFS
from metadata.jpg_metadata import JPGImageMetaData
from datetime import datetime


class DBConnect(object):  # Object 왜 붙어있지
    '''
    Extract the exif data from any image. Data includes GPS coordinates,
    Focal Length, Manufacture, and more.
    '''
    mydb = None
    fs = None

    def __init__(self, info):  # col을 여기서 받는게 좋을까
        myclient = pymongo.MongoClient(info["address"])
        self.mydb = myclient[info["name"]]
        self.mydb.authenticate(info["id"], info["password"])
        self.fs = GridFS(self.mydb)

        # print(self.image._getexif())

    def put_image(self, image_path, user_id):
        readycol = self.mydb['ready']
        count = readycol.count({'telegram_id': user_id})
        if count > 0:
            return 2  # read queue에 있는것을 의미
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        meta_data = JPGImageMetaData(image_path)
        latlng = meta_data.get_lat_lng()
        if latlng[0] is None:  # 위도 경도 안 나왔을때
            print("None입니다. 위도 경도를 입력해주세요")
            f = open(image_path, 'rb')  # 이미지가 없을 경우 예외처리가 필요로함
            image_id = self.fs.put(f)
            mycol = self.mydb['ready']
            meta = {
                'telegram_id': user_id,  # image ID, telegram ID
                'image_id': image_id
            }
            mycol.insert_one(meta)
            return 1  # read queue에 담긴것을 의미
        else:
            f = open(image_path, 'rb')  # 이미지가 없을 경우 예외처리가 필요로함

            image_id = self.fs.put(f)
            DataTime = meta_data.exif_data['DateTimeOriginal']
            # print(image_id)
            # gridfs filename
            f.close()

            meta = {
                'telegram_id': user_id,  # image ID, telegram ID
                'latitude': latlng[0],
                "longitude": latlng[1],
                'image_id': image_id,
                'DataTime': DataTime
            }
            mycol = self.mydb['images']

            # # insert the meta data
            mycol.insert_one(meta)
            return 0  # 정상 종료

    def get_image(self, user_id):
        mycol = self.mydb['images']
        image = mycol.find_one({'telegram_id': user_id})
        #
        # # get the image from gridfs
        gOut = self.fs.get(image['image_id'])
        #
        # # convert bytes to ndarray
        return gOut, image["_id"]

        # im = Image.open(gOut)

        # im.save('out2.jpg')

        # 이미지 JPG로 저장

    def delete_image(self, _id):
        mycol = self.mydb['images']
        image = mycol.find_one({'_id': _id})
        self.fs.delete(image['image_id'])
        mycol.delete_one(image)

    def put_local(self, local, user_id):

        mycol = self.mydb['ready']
        count = mycol.count({'telegram_id': user_id})
        if count > 0:
            oh_col = mycol.find_one({'telegram_id': user_id})
            latitude = local['location']['latitude']
            longitude = local['location']['longitude']
            image_id = oh_col["image_id"]
            nowDatetime = datetime.now().strftime('%Y:%m:%d %H:%M:%S')

            meta = {
                'telegram_id': user_id,  # image ID, telegram ID
                'latitude': latitude,
                "longitude": longitude,
                'image_id': image_id,
                'DataTime': nowDatetime
            }
            images_col = self.mydb['images']

            # # insert the meta data
            images_col.insert_one(meta)
            mycol.delete_one(oh_col)
            return 0
        else:
            return 1  # no ready queue

