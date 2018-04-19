# import default packages
import time
import os
import argparse
from datetime import datetime

# import 3rd part packages
import yaml
from tqdm import tqdm
import googlemaps
import matplotlib
matplotlib.use('Agg') #necessary to plot image without display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import local package
import config

gmaps = googlemaps.Client(config.key) #use your google api key here

# Set up argument parsing
parser = argparse.ArgumentParser(description='Trip profiling tool.')
parser.add_argument('route_file', type=str,
                    help='str: file name for a yaml with origin and destination specified')
parser.add_argument('--hours', default='3', type=int,
                    help='int: number of hours to run for')
args = parser.parse_args()

# Assign arguments to variables
file_name = args.route_file
hours = args.hours

# Read YAML file
with open(file_name, 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

origin = data["origin"]
destination = data["destination"]
    

def get_duration():

    now = datetime.now()
    directions = gmaps.directions(origin, destination, traffic_model="best_guess", mode="driving", departure_time=now)

    traffic_secs = directions[0]['legs'][0]['duration_in_traffic']['value']

    return now, traffic_secs

def plot_todays_traffic(data):

    times_list = data['datetime']
    durations_list = data['duration']
    durations_list /= 60

    fig, ax = plt.subplots()
    ax.plot_date(times_list, durations_list, linestyle='-', linewidth=3, marker=" ")

    ax.set_ylabel('Trip Duration (min)')
    ax.set_xlabel('Departure Time')
    ax.set_title('Traffic Profile Starting at %s' % data['datetime'].iloc[0].strftime("%Y-%m-%d %H:%M"))

    fig.autofmt_xdate()

    with plt.style.context('ggplot'):
        plt.savefig('/tmp/%s.png' % data['datetime'].iloc[0].strftime("%Y-%m-%d-%H-%M"))

    return

def main():

    # data stored is csv of day of the week, date time of instance, and duration of trip
    df = pd.DataFrame(columns=('day_of_week','datetime','duration'))

    print("Calculating trip duration over the next %s hours at 1 minute intervals." % hours)
    for i in tqdm(range(hours*60)):
        now, duration = get_duration()
        dow = datetime.today().weekday()
        df.loc[i] = [dow, now, duration]
        time.sleep(60)

    p, f = os.path.split(file_name)
    route = f.replace(".yaml", "")

    if not os.path.isfile('/tmp/traffic_%s.csv' % route):
        with open('/tmp/traffic_%s.csv' % route, 'w') as f:
            df.to_csv(f, header=True, index=False)

    else:
        with open('/tmp/traffic_%s.csv' % route, "a") as f:
            df.to_csv(f, header=False, index=False)

    plot_todays_traffic(df)

    return

main()
