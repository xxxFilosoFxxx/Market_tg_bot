import os
import asyncio
import logging
from aiogram import Bot
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db_model import Base, MediaIds
from config import API_TOKEN, DB_FILENAME

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

ID_ACCOUNT = 77777
BASE_MEDIA_PATH = './static'
engine = create_engine(f'sqlite:///{DB_FILENAME}')
if not os.path.isfile(f'./{DB_FILENAME}'):
    Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
bot = Bot(token=API_TOKEN)


async def upload_media_files(folder, method, file_attr):
    folder_path = os.path.join(BASE_MEDIA_PATH, folder)
    for filename in os.listdir(folder_path):
        if filename.startswith('.'):
            continue

        logging.info(f'Started processing {filename}')
        with open(os.path.join(folder_path, filename), 'rb') as file:
            msg = await method(ID_ACCOUNT, file, disable_notification=True)
            if file_attr == 'photo':
                file_id = msg.photo[-1].file_id
            else:
                file_id = getattr(msg, file_attr).file_id
            session = Session()
            new_item = MediaIds(file_id=file_id, filename=filename)
            try:
                session.add(new_item)
                session.commit()
            except Exception as e:
                logging.error(
                    'Couldn\'t upload {}. Error is {}'.format(filename, e))
            else:
                logging.info(
                    f'Successfully uploaded and saved to DB file {filename} with id {file_id}')
            finally:
                session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    tasks = [
        loop.create_task(upload_media_files('picture', bot.send_photo, 'photo')),
        loop.create_task(upload_media_files('videos', bot.send_video, 'video')),
        loop.create_task(upload_media_files('files', bot.send_document, 'document')),
        loop.create_task(upload_media_files('voice', bot.send_voice, 'voice')),
    ]

    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()
    Session.remove()
