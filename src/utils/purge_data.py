from src.utils.purge.csv_drop.purge_csv import purge_csv
from src.utils.purge.tables_drop.db_drop import truncate_table


def purge_data(category):
    purge_csv(category)
    truncate_table(f"results_{category}")
    # truncate_table(f"ranking_{category}")