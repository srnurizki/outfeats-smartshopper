# <<<./ Import Libraries
import json
import os
from datetime import datetime
import logging
from config.settings import REPORT_DIR

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Format Report
def format_report(product_results: dict, common_results: dict):
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'product_rag' : {
            'faithfulness' : round(product_results.get('faithulness, 0'), 4),
            'answer_relevancy' : round(product_results.get('answer_relevancy, 0'), 4),
            'context_precision' : round(product_results.get('context_precision, 0'), 4),
            'context_recall' : round(product_results.get('context_recall, 0'), 4)},
        'common_rag' : {
            'faithfulness' : round(common_results.get('faithfulness, 0'), 4),
            'answer_relevancy' : round(common_results.get('answer_relevancy, 0'), 4),
            'context_precision' : round(common_results.get('context_precision, 0'), 4),
            'context_recall' : round(common_results.get('context_recall, 0'), 4)}
    }

# <<<./ Save
def save_report(report: dict):
    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f'report_{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}.json'
    path = os.path.join(REPORT_DIR, filename)
    with open(path, 'w') as f:
        json.dump(report, f, indent = 4)
    logger.info(f'Saved Report to {path}')
    return path

# <<<./ Print
def print_report(report: dict):
    print('>>>>> RAG Evaluation Report <<<<<')
    print(f'Timestamp: {report["timestamp"]}')
    for pipeline_name, metrics in report.items():
        if pipeline_name == 'timestamp':
            continue
        print(f'\n{pipeline_name.upper()}')
        for metric, value in metrics.items():
            print(f'  {metric}: {value}')
    print('>>>>> End of Report <<<<<')

