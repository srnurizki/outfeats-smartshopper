# <<<./ Import Libraries
import pandas as pd
from ast import literal_eval
from config.settings import CM_RAW_PATH, CM_CLEANED_PATH
import logging
from tools.timer import timer

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Load Data
@timer
def load_data():
    df = pd.read_csv(CM_RAW_PATH)
    print(f'Shape: {df.shape[0]} Rows, {df.shape[1]} Columns')
    return df

# <<<./ Clean Features
@timer
def clean_data(df):
    before = len(df)
    df = df.dropna()
    logger.info(f'NaN values: \n{df.isna().sum()}')
    df['instruction'] = [' '.join(d.split()) for d in df['instruction']]
    df['response'] = [' '.join(d.split()) for d in df['response']]
    df.drop_duplicates(inplace=True)
    logger.info(f'Duplicates: {df.duplicated().sum()}')
    df['flags'] = [list(f) for f in df['flags']]
    after = len(df)
    return df, before, after

# <<<./ Save to CSV
@timer
def save(df):
    df.to_csv(CM_CLEANED_PATH, sep=';', index=True)
    return None

# <<<./ Init
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info(f'Initializing preprocessing...')
    df = load_data()
    logger.info(f'Data successfully loaded!')
    df, before, after = clean_data(df)
    save(df)
    logger.info(f'Data preprocessing is done. Rows: {df.shape[0]} | Columns: {df.shape[1]} | Dropped: {((before - after)/after * 100):.3f}%')
    logger.info(f'Saved to {CM_CLEANED_PATH}')




