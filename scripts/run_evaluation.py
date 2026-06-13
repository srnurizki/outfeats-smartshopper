# <<<./ Import Libraries
from monitoring.evaluator import run_eval_product, run_eval_commons
from monitoring.report import format_report, save_report, print_report
import logging

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Init
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info('Running ProductRAG Evaluation...')
    product_results = run_eval_product()

    logger.info('Running CommonsRAG Evaluation...')
    common_results = run_eval_commons()

    report = format_report(product_results, common_results)
    print_report(report)
    path = save_report(report)
    logger.info(f'Evaluation completed. Saved report to {path}')