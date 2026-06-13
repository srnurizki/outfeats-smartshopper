# <<<./ Import Libraries
import pandas as pd
from ast import literal_eval
from config.settings import SH_RAW_PATH, SH_CLEANED_PATH
import logging
from tools.timer import timer

# <<<./ Instantiate Logger
logger = logging.getLogger(__name__)

# <<<./ Load Data
@timer
def load_data():
    df = pd.read_csv(SH_RAW_PATH, sep=';', encoding='latin-1')
    print(f'Shape: {df.shape[0]} Rows, {df.shape[1]} Columns')
    return df

# <<<./ Clean Features
@timer
def clean_data(df):
    before = len(df)
    df['price'] = df['price'].str.extract(r'(\d+\.?\d*)')[0].astype('float')
    df['sku'] = df['sku'].str.removeprefix('SKU:').str.strip().fillna('unlisted')
    df['size'] = df['size'].fillna('unlisted')
    df['brand'] = df['brand'].fillna('unlisted').str.replace('\xa0', ' ')
    df = df.dropna(subset=['price']).reset_index(drop=True)
    after = len(df)
    return df, before, after

# <<<./ Parse Description
@timer
def parse_desc(df):
    assert df['description'].isna().sum() == 0, 'Missing values not removed entirely!'
    df['description'] = df['description'].apply(literal_eval)
    for i, row in enumerate(df['description']):
        flatten = {k: v for d in row for k, v in d.items()}
        df.at[i, 'color'] = flatten.get('Color', 'unlisted')
        df.at[i, 'pattern'] = flatten.get('Pattern Type', 'unlisted')
        df.at[i, 'fabric'] = flatten.get('Fabric', 'unlisted')
        df.at[i, 'style'] = flatten.get('Style', 'unlisted')
    return df

# <<<./ Parse Size
@timer
def parse_size(df):
    assert df['size'].isna().sum() == 0, 'Missing values not removed entirely!'
    df['size'] = df['size'].apply(lambda x: [s.strip() for s in str(x).split(',')] if x != 'unlisted' else ['unlisted'])
    return df

# <<<./ Feature Selection
@timer
def feature_selection(df):
    df.drop(columns='images', inplace=True)
    return df

# <<<./ Save to CSV
@timer
def save(df):
    df = df.sample(n=35000, random_state=42).reset_index(drop=True)
    df.to_csv(SH_CLEANED_PATH, sep=';', index=True)
    return None

# <<<./ Init
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info(f'Initializing preprocessing...')
    df = load_data()
    logger.info(f'Data successfully loaded!')
    df, before, after = clean_data(df)
    logger.info(f'Data has been cleaned')
    df = parse_desc(df)
    logger.info(f'Description has been parsed')
    df = parse_size(df)
    logger.info(f'Size has been parsed')
    df = feature_selection(df)
    save(df)
    logger.info(f'Data preprocessing is done. Rows: {df.shape[0]} | Columns: {df.shape[1]} | Dropped: {((before - after)/after * 100):.3f}%')
    logger.info(f'Saved to {SH_CLEANED_PATH}')




