import logging

from colorama import Fore
from InquirerPy import prompt

from simpleval.consts import LOGGER_NAME
from simpleval.evaluation.judges.judge_provider import JudgeProvider
from simpleval.utilities.console import print_boxed_message, print_list


def judge_explorer_command():
    logger = logging.getLogger(LOGGER_NAME)
    print_boxed_message('Explore judge information')

    judges = JudgeProvider.list_judges(filter_internal=True)
    if not judges:
        logger.warning(f'{Fore.YELLOW}No judges found!{Fore.RESET}')
        return

    questions = [{'type': 'list', 'name': 'selected_judge', 'message': 'Select a judge:', 'choices': judges}]
    answers = prompt(questions)
    selected_judge = answers['selected_judge']

    logger.info('')
    logger.info(f'Selected judge: {selected_judge}')

    judge = JudgeProvider.get_judge(judge_name=selected_judge)
    logger.info('')

    logger.info(f'{Fore.CYAN}Judge name: {Fore.YELLOW}{judge.name}{Fore.RESET}')
    logger.info(f'{Fore.CYAN}Default model id: {Fore.YELLOW}{judge.model_id}{Fore.RESET}')
    logger.info('')

    print_list(title='Supported metrics', items=judge.list_metrics())
    logger.info(f'{Fore.CYAN}Authentication requirements: \n{Fore.YELLOW}{judge.preliminary_checks_explanation()}{Fore.RESET}')
    logger.info('')
    print_list(title='Supported model ids', items=judge.supported_model_ids)
    logger.info(f'{Fore.CYAN}NOTE: It is possible to use unsupported model ids, just make sure they are compatible{Fore.RESET}')
