import logging
import uuid
import typing
import config

from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

CATALOG = (('Первый продавец', 'sub'),  # prod_1
           ('Второй продавец', 'sub'),
           ('Третий продавец', 'sub')
           )


POSTS = {
    str(uuid.uuid4()): {
        'title': '📖Инсткрукция к применению',
        'body': '☑️Мы собрали <b>продавцов самых крутых услуг</b> и товаров на рынке Telegram.\n\n'
                '☑️Для того,что бы вам <b>подробнее рассказали</b> про услугу-пишите продавцу в личные сообщения.\n\n'
                '☑️Все продавцы <b>имеют репутацию</b> и многолетние отзывы.\n\n'
                '☑️Если у вас <b>вышло недопонимание</b> с продавцов-пишите администрации БОТА.\n\n'
                '☑️Использование  услугами <b>не нарушает законов РФ</b>.\n\n'
                '☑️Перед работой с продавцом <b>проконсультируйтесь</b> с администрацией БОТА.',
        'banner': config.BANNERS['banner_4'],
        'keys': (('🔍Каталог услуг и товаров', 'catalog'), ('💰Оплатить подписку', 'sub'))
    },
    str(uuid.uuid4()): {
        'title': '🔍Каталог услуг и товаров',
        'body': '⚠️Тут собраны лучшие и надеждые продавцы самых различных услуг.\n\n'
                '👁Внимательно изучи каждого-он пригодиться.\n\n'
                '❓Если есть вопрос-пиши поддержке!\n\n'
                '♻️Мы каждый день ищем для вас новые услуги и добавляем их в бота',
        'banner': config.BANNERS['banner_5'],
        'keys': CATALOG
    },
    str(uuid.uuid4()): {
        'title': '📩Отправить жалобу',
        'body': '📎 Перед подачей жалобы просим Вас ознакомиться правилами заполнения анкеты.\n\n'
                '❗️Жалоба будет обрабатываться в тех случаях, когда она оформлена правильно.',
        'banner': config.BANNERS['banner_6'],
        'keys': (('Правила подачи жалобы', 'complaint_rules'), ('📄Подать жалобу', 'contact'))
    },
    str(uuid.uuid4()): {
        'title': '🛡Поддержка 24/7',
        'body': '☑️Если у вас возник вопрос или вам нужна консультация по '
                'продавцам и использованию услуг в боте - пишите @{}'.format(config.MANE_CONTACT),
        'banner': config.BANNERS['banner_7'],
        'keys': (('💬Консультация', 'contact'), ('🔍Каталог услуг и товаров', 'catalog'))
    },
    str(uuid.uuid4()): {
        'title': '⚔️Стать продавцом',
        'body': '📬 Анкета\n'
                '└  Заполните необходимую информацию указанную в форме.\n\n'
                '📝 Форма\n'
                '└ Что Вы желаете продвигать?\n'
                '└ Как давно Вы в своей сфере?\n'
                '└ Есть поручитель/ответчик?\n'
                '└ Отзывы сюда или в поддержку.\n'
                '└ Пройдены проверки на других ресурсах?\n'
                '└ Ветки на форумах (ссылки)\n\n'
                '⚠️  Присылать анкету 1 сообщением.\n'
                '└❗️ Без отзывов и веток анкета не пройдёт проверку',
        'banner': config.BANNERS['avatar'],
        'keys': (('📝Отправить анкету', 'contact'), )
    },
    str(uuid.uuid4()): {
        'title': '🌎Наш MARKETPLACE',
        'body': '<b>Лучшая</b> доска объявлений в Telegram.\n\n'
                'Подать объявление бесплатно может каждый,'
                'у кого есть подписка на нашего бота.\n\n'
                'Заходи - изучай!\n'
                '{}'.format(config.URL_CHAT),
        'banner': config.BANNERS['avatar'],
        'keys': (('💬Консультация', 'contact'), )
    }
}

posts_cb = CallbackData('post', 'id', 'action')  # post:<id>:<action>


def add_keyboard_markup(text_and_data, row_width: int) -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup(row_width=row_width)
    row_buttons = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.add(*row_buttons)
    return keyboard_markup


def get_keyboard() -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup()
    for post_id, post in POSTS.items():
        keyboard_markup.add(
            types.InlineKeyboardButton(
                post['title'],
                callback_data=posts_cb.new(id=post_id, action='view')),
        )
    return keyboard_markup


def format_post(post_id: str, post: dict, row_width: int) -> (str, types.InlineKeyboardMarkup):
    text = md.text(
        md.hbold(post['title']),
        '',
        md.text(post['body']),
        sep='\n',
    )
    keyboard_markup = types.InlineKeyboardMarkup(row_width=row_width)
    row_buttons = (types.InlineKeyboardButton(post_text, callback_data=posts_cb.new(id=post_id, action=data))
                   for post_text, data in post['keys'] if data != 'contact')
    keyboard_markup.add(*row_buttons)
    for post_text, data in post['keys']:
        if data == 'contact':
            keyboard_markup.add(types.InlineKeyboardButton(post_text, url=config.URL_MANE_CONTACT))
    keyboard_markup.add(types.InlineKeyboardButton('🔗Вернуться к главному меню',
                                                   callback_data=posts_cb.new(id='-', action='list')))
    return text, keyboard_markup


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    text_and_data = (('Ознакомиться с правилами', 'read_the_rules_1'),)
    keyboard_markup = add_keyboard_markup(text_and_data, 1)
    text_for_agreement = f'Добро пожаловать в сервис {config.APP_NAME}'
    await bot.send_photo(message.from_user.id, photo=config.BANNERS['banner_2'], caption=text_for_agreement,
                         reply_markup=keyboard_markup)


@dp.callback_query_handler(text='repeat')
async def repeat_callback_handler(query: types.CallbackQuery):
    text_and_data = (('Ознакомиться с правилами', 'read_the_rules_1'),)
    keyboard_markup = add_keyboard_markup(text_and_data, 1)
    text_for_agreement = f'Добро пожаловать в сервис {config.APP_NAME}'
    await query.message.edit_media(media=types.InputMedia(media=config.BANNERS['banner_2']))
    await query.message.edit_caption(caption=text_for_agreement, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='read_the_rules_1')
async def inline_agree_answer_callback_handler_1(query: types.CallbackQuery):
    text_and_data = (('Читать далее', 'read_the_rules_2'),)
    keyboard_markup = add_keyboard_markup(text_and_data, 1)
    text_for_agreement = 'Администрация Бота «{}» предоставляет Вам доступ к использованию Бота и его ' \
                         'функционала на условиях, являющихся предметом настоящих Правил пользования Ботом.\n\n' \
                         'В этой связи Вам необходимо внимательно ознакомиться с условиями настоящих Правил, ' \
                         'которые рассматриваются Администрацией Бота как публичная оферта в соответствии со ст. 437 ' \
                         'Гражданского кодекса Российской Федерации.\n\n' \
                         '⚠️ Приступая к пользованию Ботом, Вы соглашаетесь с нижеследующими правилами:\n\n' \
                         '— Бот носит исключительно информационный характер. За действия Пользователей Администрация ' \
                         'ответственности не несёт'.format(config.APP_NAME)
    await query.message.edit_media(media=types.InputMedia(media=config.BANNERS['banner_1']))
    await query.message.edit_caption(caption=text_for_agreement, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='read_the_rules_2')
async def inline_agree_answer_callback_handler_2(query: types.CallbackQuery):
    text_and_data = (('Читать далее', 'read_the_rules_3'),)
    keyboard_markup = add_keyboard_markup(text_and_data, 1)
    text_for_agreement = '— Администрация Бота оставляет за собой право защищать честь и интересы Пользователей, ' \
                         'и ограждать их от нарушителей Правил путём ограничения таковым доступа к Боту, ' \
                         'вплоть до передачи информации о нарушении Администрации мессенджера «Telegram»\n\n' \
                         '— Пользователь несёт личную ответственность за любую информацию, которую размещает в Боте, ' \
                         'сообщает другим Пользователям, а также за любые взаимодействия с другими Пользователями, ' \
                         'осуществляемые на свой риск\n\n' \
                         '— В случае несогласия Пользователя с настоящими Правилами или их обновлениями,  ' \
                         'Пользователь обязан отказаться от использования Бота, проинформировав об этом ' \
                         'Администрацию Бота в установленном порядке'
    await query.message.edit_caption(caption=text_for_agreement, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='read_the_rules_3')
async def inline_agree_answer_callback_handler_3(query: types.CallbackQuery):
    text_and_data = (('✅Соглашаюсь', posts_cb.new(id='-', action='list')),
                     ('Покинуть сервис', 'repeat'),)
    keyboard_markup = add_keyboard_markup(text_and_data, 2)
    text_for_agreement = '— Все объекты, размещенные в Боте, в том числе элементы дизайна, текст, графические ' \
                         'изображения, иллюстрации, скрипты, программы, музыка, звуки и другие объекты и их ' \
                         'подборки, являются объектами исключительных прав Администрации и других правообладателей, ' \
                         'все права на эти объекты защищены\n\n' \
                         '— Администрация Бота не несет ответственность в случае потери средств и других предметов ' \
                         'ценности в случаях, когда кто-либо из участников Бота,  приобретает платные услуги у ' \
                         'другого участника Бота без использования Гарант-сервиса от Администрации Бота.\n\n' \
                         '⚠️ Пользуясь Ботом «{}», Вы автоматически принимаете условия Соглашения в полном ' \
                         'объёме.'.format(config.APP_NAME)
    # TODO: при соглашении и/или подписке закидывать айди пользователя (чата) в БД
    await query.message.edit_caption(caption=text_for_agreement, reply_markup=keyboard_markup)


@dp.callback_query_handler(posts_cb.filter(action='view'))
async def query_view(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    post_id = callback_data['id']

    post = POSTS.get(post_id, None)
    if not post:
        return await query.answer('Ошибка, перезапустите бота!')

    text, keyboard_markup = format_post(post_id, post, 1)
    await query.message.edit_media(media=types.InputMedia(media=post['banner']))
    await query.message.edit_caption(caption=text, reply_markup=keyboard_markup)


@dp.callback_query_handler(posts_cb.filter(action='list'))
async def query_show_list(query: types.CallbackQuery):
    await query.message.edit_media(media=types.InputMedia(media=config.BANNERS['banner_3']))
    await query.message.edit_caption(caption='👋Доброго времени суток, ты находишься в {}.\n\n'
                                             '👀Внимательно прочти каждую кнопку снизу!'.format(config.APP_NAME),
                                     reply_markup=get_keyboard())


@dp.callback_query_handler(posts_cb.filter(action='sub'))  # ['prod_1', 'prod_2', 'prod_3']
async def query_show_sub(query: types.CallbackQuery):
    # text_and_data = (('Оплатить', 'pay_sub'),)
    # keyboard_markup = add_keyboard_markup(text_and_data, 1)
    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.add(types.InlineKeyboardButton('💰Оплатить', url=config.URL_MANE_CONTACT))
    keyboard_markup.add(types.InlineKeyboardButton('🔗Вернуться к главному меню',
                                                   callback_data=posts_cb.new(id='-', action='list')))
    text = '🚸Мы старались и делали для вас этого бота, чтобы вы могли больше ' \
           'не переживать за порядочность и качество!\n\n' \
           '⚠️Чтобы пользоваться услугами нашего бота нужно оплатить подписку.\n\n' \
           'Нажми на <b>кнопку ниже</b>, вам расскажут более подробно преимущества нашего бота.'
    await query.message.edit_media(media=types.InputMedia(media=config.BANNERS['banner_8']))
    await query.message.edit_caption(caption=text, reply_markup=keyboard_markup, parse_mode='HTML')


@dp.callback_query_handler(posts_cb.filter(action='complaint_rules'))
async def query_show_rules(query: types.CallbackQuery):
    text = md.text(
        md.hbold('Жалоба будет одобрена, если ваш случай подходит под описание, указанное ниже:\n\n'),
        md.quote_html('1. Статус пользователя: Кидала.\n\n'
                      'Человек кинул на деньги/товар или другой предмет, имеющий определенную материальную стоимость.\n'
                      '(Необходимо указать причину добавления: Кидок).\n'
                      'В описании жалобы указать сумму ущерба, причастные лица, '
                      'предмет спора и предоставить доказательства при оформлении заявки.\n\n'
                      '2. Статус пользователя: Отказ работать через проверенный гарант-сервис!\n\n'
                      'Человек отказывается работать через проверенный гарант-сервис/навязывает только своего гаранта, '
                      'который не вызывает доверия у клиента.\n'
                      '(Необходимо указать причину добавления: Отказ работать через гаранта).\n'
                      'В описании указать причину жалобы и предоставить все необходимые доказательства.')
    )
    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.add(types.InlineKeyboardButton('📄Подать жалобу', url=config.URL_MANE_CONTACT))
    keyboard_markup.add(types.InlineKeyboardButton('🔗Вернуться к главному меню',
                                                   callback_data=posts_cb.new(id='-', action='list')))
    await query.message.edit_caption(caption=text, reply_markup=keyboard_markup)


@dp.callback_query_handler(posts_cb.filter(action='catalog'))
async def query_show_catalog(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    post_id = callback_data['id']

    post = POSTS.get(post_id, None)
    if not post:
        return await query.answer('Ошибка, перезапустите бота!')

    text = md.text(
        md.hbold('🔍Каталог услуг и товаров\n\n'),
        md.text('⚠️Тут собраны лучшие и надеждые продавцы самых различных услуг.\n\n'
                '👁Внимательно изучи каждого-он пригодиться.\n\n'
                '❓Если есть вопрос-пиши поддержке!\n\n'
                '♻️Мы каждый день ищем для вас новые услуги и добавляем их в бота',)
    )
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    row_buttons = (types.InlineKeyboardButton(post_text, callback_data=posts_cb.new(id=post_id, action=data))
                   for post_text, data in CATALOG)
    keyboard_markup.add(*row_buttons)
    keyboard_markup.add(types.InlineKeyboardButton('🔗Вернуться к главному меню',
                                                   callback_data=posts_cb.new(id='-', action='list')))
    await query.message.edit_media(media=types.InputMedia(media=config.BANNERS['banner_5']))
    await query.message.edit_caption(caption=text, reply_markup=keyboard_markup)


# @dp.callback_query_handler(text='agree')
# async def inline_agree_answer_callback_handler(query: types.CallbackQuery):
#     answer_data = query.data
#     await query.answer(f'Вы ответили {answer_data!r}')
#     if answer_data == 'agree':
#         text = 'Great, me too!'
#     else:
#         text = f'Неизвестная ошибка: {answer_data!r}!'
#     await bot.send_message(query.from_user.id, text)


# --------------------------------------------------------


# @dp.callback_query_handler(text='no')
# @dp.callback_query_handler(text='yes')
# async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
#     answer_data = query.data
#     # always answer callback queries, even if you have nothing to say
#     await query.answer(f'You answered with {answer_data!r}')
#
#     if answer_data == 'yes':
#         text = 'Great, me too!'
#     elif answer_data == 'no':
#         text = 'Oh no...Why so?'
#     else:
#         text = f'Unexpected callback data {answer_data!r}!'
#
#     await bot.send_message(query.from_user.id, text)


# @dp.message_handler()
# async def echo(message: types.Message):
#     # old style:
#     # await bot.send_message(message.chat.id, message.text)
#
#     await message.answer(message.text)


# --------------------------------------

# POSTS = {
#     str(uuid.uuid4()): {
#         'title': f'Post {index}',
#         'body': 'Lorem ipsum dolor sit amet, '
#                 'consectetur adipiscing elit, '
#                 'sed do eiusmod tempor incididunt ut '
#                 'labore et dolore magna aliqua',
#         'votes': random.randint(-2, 5),
#     } for index in range(1, 6)
# }
#
# posts_cb = CallbackData('post', 'id', 'action')  # post:<id>:<action>
#
#
# def get_keyboard() -> types.InlineKeyboardMarkup:
#     """
#     Generate keyboard with list of posts
#     """
#     markup = types.InlineKeyboardMarkup()
#     for post_id, post in POSTS.items():
#         markup.add(
#             types.InlineKeyboardButton(
#                 post['title'],
#                 callback_data=posts_cb.new(id=post_id, action='view')),
#         )
#     return markup
#
#
# def format_post(post_id: str, post: dict) -> (str, types.InlineKeyboardMarkup):
#     text = md.text(
#         md.hbold(post['title']),
#         md.quote_html(post['body']),
#         '',  # just new empty line
#         f"Votes: {post['votes']}",
#         sep='\n',
#     )
#
#     markup = types.InlineKeyboardMarkup()
#     markup.row(
#         types.InlineKeyboardButton('👍', callback_data=posts_cb.new(id=post_id, action='like')),
#         types.InlineKeyboardButton('👎', callback_data=posts_cb.new(id=post_id, action='dislike')),
#     )
#     markup.add(types.InlineKeyboardButton('<< Back', callback_data=posts_cb.new(id='-', action='list')))
#     return text, markup
#
#
# @dp.message_handler(commands='start')
# async def cmd_start(message: types.Message):
#     await message.reply('Posts', reply_markup=get_keyboard())
#
#
# @dp.callback_query_handler(posts_cb.filter(action='list'))
# async def query_show_list(query: types.CallbackQuery):
#     await query.message.edit_text('Posts', reply_markup=get_keyboard())
#
#
# @dp.callback_query_handler(posts_cb.filter(action='view'))
# async def query_view(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
#     post_id = callback_data['id']
#
#     post = POSTS.get(post_id, None)
#     if not post:
#         return await query.answer('Unknown post!')
#
#     text, markup = format_post(post_id, post)
#     await query.message.edit_text(text, reply_markup=markup)
#
#
# @dp.callback_query_handler(posts_cb.filter(action=['like', 'dislike']))
# async def query_post_vote(query: types.CallbackQuery, callback_data: typing.Dict[str, str]):
#     try:
#         await dp.throttle('vote', rate=1)
#     except Throttled:
#         return await query.answer('Too many requests.')
#
#     post_id = callback_data['id']
#     action = callback_data['action']
#
#     post = POSTS.get(post_id, None)
#     if not post:
#         return await query.answer('Unknown post!')
#
#     if action == 'like':
#         post['votes'] += 1
#     elif action == 'dislike':
#         post['votes'] -= 1
#
#     await query.answer('Vote accepted')
#     text, markup = format_post(post_id, post)
#     await query.message.edit_text(text, reply_markup=markup)


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True  # errors_handler must return True if error was handled correctly


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
