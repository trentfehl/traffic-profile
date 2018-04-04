import googlemaps
import time
import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
import config

gmaps = googlemaps.Client(config.key) #use your google api key here

########################################################
""" Change these variables to configure code """
origin = config.origin
destination = config.destination
hours = 1 #number of hours to profile for
########################################################

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
    ax.plot_date(times_list, durations_list, linestyle='--')

    ax.set_xlabel('Departure Time')
    ax.set_ylabel('Trip Duration (min)')
    ax.set_title('Morning Traffic Profile for %s' % datetime.now().strftime("%Y-%m-%d"))

    fig.autofmt_xdate()
    plt.savefig('/tmp/%s.png' % datetime.now().strftime("%Y-%m-%d"))

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

    if not os.path.isfile('/tmp/traffic_data.csv'):
        with open('/tmp/traffic_data.csv', 'w') as f:
            df.to_csv(f, header=True, index=False)

    else:
        with open('/tmp/traffic_data.csv', "a") as f:
            df.to_csv(f, header=False, index=False)

    plot_todays_traffic(df)

    return

main()
