import pandas as pd
from sqlalchemy import create_engine
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL_PD)

def load_data():
    df = pd.read_csv('src/analytics/scripts/data.csv', sep=';')
    df = df.drop(df.columns[0], axis=1) 
    df.columns = [col.lower() for col in df.columns]
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df.to_sql(
        name="respondent_stat",
        con=engine,
        if_exists="append",
        index=False, 
        chunksize=5000,
        method="multi",
    )

if __name__ == "__main__":
    load_data()