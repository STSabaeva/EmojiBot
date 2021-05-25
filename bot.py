from data import emoji
from db_schema import Users, Sessions, Messages, session
from datetime import datetime
import time
from save_thread_result import ThreadWithResult


def check_answer(user_message):
    """ Проверяет, является ли введенный ответ корректным, и если да,
    то возвращает ту эмоцию, которую он символизирует. """
    try:
        answer = emoji[user_message]
        return answer
    except Exception:
        return False


user_id = ''


def check_name(user_name):
    """ Проверяет, существует ли пользователь с таким именем в базе,
    если нет, создаёт его. Извлекает user_id."""
    global user_id
    user = session.query(Users).filter_by(user_name=user_name).first()
    if not user:
        new = Users(user_name)
        session.add(new)
        session.commit()
        user_id = new.user_id
        return False
    else:
        user_id = user.user_id
        return True


def my_input():
    return input('Введите эмоджи: \n')


# Начало. Записывается информация о сесиии
user_name = input("Привет, незнакомец, как я могу к тебе обращаться?\n")
if check_name(user_name):
    print(f"Ого, кажется, ты уже был здесь, {user_name}! Если ты хочешь "
          f"снова пообщаться, пожалуйста, опиши своё состояние с "
          f"помощью эмоджи (не используй кавычки)")
else:
    print(
        f"Приятно познакомиться, {user_name}! Если ты хочешь пообщаться, "
        f"пожалуйста, опиши своё состояние с помощью эмоджи "
        f"(не используй кавычки)")

user_messages = {}
i = 0
new_session = Sessions(datetime.utcnow(), datetime.utcnow())
session.add(new_session)
session.commit()
session_id = new_session.session_id
message_time = datetime.utcnow()

while True:
    # Создаётся второй поток для получения информации от пользователя (в
    # первом потоке одновременно создается таймер, чтобы избежать блокировки
    # input
    new_thread = ThreadWithResult(target=my_input)
    new_thread.start()

    while (datetime.utcnow() - message_time).seconds / 60 <= 1 and \
            new_thread.is_alive():
        time.sleep(3)

    if not new_thread.is_alive():
        # Вариант, когда пользователь ввел ответ
        user_message = getattr(new_thread, 'result', None)
        message = Messages(user_id=user_id, session_id=session_id,
                           message_time=datetime.utcnow(), text=user_message)
        message_time = message.message_time
        i = i + 1
        session.add(message)
        session.commit()
        user_messages[i] = check_answer(user_message)

        if user_messages[i]:
            # Оценка первого эмоджи
            if i == 1 and user_messages[i] == 'Радость':
                print(f'У тебя отличное настроение, {user_name}!')
            elif i == 1 and user_messages[i] == 'Грусть':
                print(f'{user_name}, не грусти!')
            elif i == 1 and user_messages[i] == 'Раздражение/злость':
                print(f'{user_name}, пожалуйста, не злись!')

            # Переход к радости
            elif user_messages[i] == 'Радость' and \
                    user_messages[i - 1] == 'Раздражение/злость':
                print(f'{user_name}, я рад, что ты больше не злишься!')
            elif user_messages[i] == 'Радость' and user_messages[
                i - 1] == 'Грусть':
                print(f'{user_name}, я рад, что ты больше не грустишь!')
            elif user_messages[i] == 'Радость' and user_messages[
                i - 1] == 'Радость':
                print(f'Кажется, твоё настроение стало еще лучше, {user_name}!')

            # Переход к грусти
            elif user_messages[i] == 'Грусть' and \
                    user_messages[i - 1] == 'Раздражение/злость':
                print(f'{user_name}, я рад, что ты больше не злишься, но вижу, '
                      f'что теперь тебе стало грустно!')
            elif user_messages[i] == 'Грусть' and user_messages[
                i - 1] == 'Радость':
                print(f'Ой, {user_name}, кажется, ты загрустил!')
            elif user_messages[i] == 'Грусть' and user_messages[
                i - 1] == 'Грусть':
                print(f'Ты всё еще грустишь, {user_name}!')

            # Переход к злости
            elif user_messages[i] == 'Раздражение/злость' and \
                    user_messages[i - 1] == 'Раздражение/злость':
                print(f'{user_name}, кажется, ты все еще злишься!')
            elif user_messages[i] == 'Раздражение/злость' and \
                    user_messages[i - 1] == 'Радость':
                print(f'Ой, {user_name}, вижу, ты разозлился!')
            elif user_messages[i] == 'Раздражение/злость' and \
                    user_messages[i - 1] == 'Грусть':
                print(
                    f'Я рад, что ты больше не грустишь, {user_name}, но вижу, '
                    f'что теперь ты злишься!')
        else:
            print("Извини, но я тебя не понимаю :( \nБеседа обнуляется")
            edited_session = session.query(Sessions).filter_by(
                session_id=session_id).one()
            edited_session.end_time = datetime.utcnow()
            session.add(edited_session)
            session.commit()
            session.close()
            break
    else:
        edited_session = session.query(Sessions).filter_by(
            session_id=session_id).one()
        edited_session.end_time = datetime.utcnow()
        session.add(edited_session)
        session.commit()
        session.close()
        print('Ты слишком долго не отвечаешь, я вынужден закрыть сессию!')
        break

