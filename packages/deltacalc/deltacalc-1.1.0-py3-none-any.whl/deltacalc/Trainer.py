from IPython.display import display
from .Main import RandomDerivative, RandomIntegral, check

class Trainer:
    @staticmethod
    def practice_derivatives(num):
        for i in range(num):
            display(f'Problem {i + 1}:')

            RandomDerivative.init()
            e = RandomDerivative.generate()
            display(RandomDerivative.equation(e))
            display(RandomDerivative.question())

            correct_answer = RandomDerivative.answer(e)

            while True:
                try:
                    answer = input('Enter your answer: \n')
                    print(f'Your answer: {answer}')

                    print('Correct!' if check(answer, correct_answer) else 'Incorrect!')

                    break

                except:
                    print('Invalid input. Please try again.')

            print('Correct answer: ')
            display(correct_answer)

    @staticmethod
    def practice_integrals(num):
        for i in range(num):
            display(f'Problem {i + 1}:')

            RandomIntegral.init()
            e = RandomIntegral.generate()
            display(RandomIntegral.equation(e))
            display(RandomIntegral.question())
            correct_answer = RandomIntegral.answer(e)

            while True:
                try:
                    answer = input('Enter your answer: \n')
                    print(f'Your answer: {answer}')

                    print('Correct!' if check(answer, correct_answer) else 'Incorrect!')

                    break

                except:
                    print('Invalid input. Please try again.')

            print('Correct answer: ')
            display(correct_answer)