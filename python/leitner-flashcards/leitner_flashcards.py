from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Flashcard(Base):
    __tablename__ = "flashcard"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    box = Column(Integer, default=1)
    sessions_since_last_studied = Column(Integer, default=0)

    def __repr__(self):
        return f'id: {self.id}; question: {self.question}; answer: {self.answer}'


def load_database(database_name):
    engine = create_engine(f'sqlite:///{database_name}?check_same_thread=False', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, session.query(Flashcard).all()


def add_flashcards(session, last_flashcard_id):
    while True:
        print('1. Add a new flashcard')
        print('2. Exit')
        user_choice = input()
        if user_choice == '1':
            while True:
                new_question = input("Question:\n")
                if new_question.strip():
                    break

            while True:
                new_answer = input("Answer:\n")
                if new_answer.strip():
                    break

            last_flashcard_id += 1
            new_flashcard = Flashcard(id=last_flashcard_id, question=new_question, answer=new_answer,
                                      box=1, sessions_since_last_studied=0)
            session.add(new_flashcard)
            session.commit()

        elif user_choice == '2':
            break

        else:
            print(f'{user_choice} is not an option')


def update_flashcard(session, current_flashcard):
    while True:
        print('press "d" to delete the flashcard:')
        print('press "e" to edit the flashcard:')
        user_choice = input()

        if user_choice == 'd':
            session.delete(current_flashcard)
            session.commit()
            break

        elif user_choice == 'e':
            print(f'current question: {current_flashcard.question}')
            new_question = input('please write a new question:')
            if new_question.strip():
                current_flashcard.question = new_question
                session.commit()

            print(f'current answer: {current_flashcard.answer}')
            new_answer = input('please write a new answer:')
            if new_answer.strip():
                current_flashcard.answer = new_answer
                session.commit()
            break


        else:
            print(f'{user_choice} is not an option')


def check_whether_learned(session, current_flashcard):
    while True:
        print('press "y" if your answer is correct:')
        print('press "n" if your answer is wrong:')
        user_choice = input()
        if user_choice == 'y':
            if current_flashcard.box >= 3:
                session.delete(current_flashcard)
            else:
                current_flashcard.box += 1
            session.commit()
            break

        elif user_choice == 'n':
            current_flashcard.box = 1
            session.commit()
            break

        else:
            print(f'{user_choice} is not an option')


def study_flashcards(session):
    flashcards = session.query(Flashcard).all()
    not_studied_flashcard = 0

    for current_flashcard in flashcards:
        if current_flashcard.sessions_since_last_studied < current_flashcard.box - 1:
            current_flashcard.sessions_since_last_studied += 1
            not_studied_flashcard += 1
            if not_studied_flashcard == len(flashcards):
                print('There are no flashcards to practice!')
                break
            session.commit()
            continue


        print(f"Question: {current_flashcard.question}")
        while True:
            print('press "y" to see the answer:')
            print('press "n" to skip:')
            print('press "u" to update:')
            user_choice = input()

            if user_choice == 'y':
                print(f'Answer: {current_flashcard.answer}')
                check_whether_learned(session, current_flashcard)
                current_flashcard.sessions_since_last_studied = 0
                session.commit()
                break

            elif user_choice == 'n':
                check_whether_learned(session, current_flashcard)
                current_flashcard.sessions_since_last_studied = 0
                session.commit()
                break

            elif user_choice == 'u':
                update_flashcard(session, current_flashcard)
                break

            else:
                print(f'{user_choice} is not an option')


def main():
    session, flashcards = load_database('flashcard.db')
    try:
        last_flashcard_id = int(flashcards[-1].id)
    except IndexError:
        last_flashcard_id = 0

    while True:
        print('1. Add flashcards')
        print('2. Practice flashcards')
        print('3. Exit')

        user_choice = input()

        if user_choice == '1':
            add_flashcards(session, last_flashcard_id)

        elif user_choice == '2':
            _, flashcards = load_database('flashcard.db')
            if flashcards:
                study_flashcards(session)
            else:
                print("There are no flashcards to practice!")

        elif user_choice == '3':
            print('Bye!')
            break
        else:
            print(f'{user_choice} is not an option')


main()
