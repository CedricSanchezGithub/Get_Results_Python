import os

def purge_csv(category):

    folder = "data"
    csv_filename = f"results_{category}.csv"
    csv_filepath = os.path.join(folder, csv_filename)

    if os.path.exists(csv_filepath):
        os.remove(csv_filepath)
        print(f"Removed {csv_filepath}")
    else:
        return