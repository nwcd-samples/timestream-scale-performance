import argparse
import json
import random
import signal
import string
import sys
import time
from collections import namedtuple

import boto3
import numpy as np
import uuid


powertrainState = 'powertrain_state'
ignition_state = 'ignition_state'
bms_soc2 = 'bms_soc2'
odo = 'odo'
speed = 'speed'
gear = 'gear'
engine_rpm = 'engine_rpm'
systolic='systolic'
diastolic = 'diastolic'
temp = 'temp'
pressureLevel="pressureLevel"


measuresForMetrics = [systolic, diastolic, pressureLevel, temp,powertrainState, ignition_state, bms_soc2, odo, speed, gear, engine_rpm]

remainingmetrics = [powertrainState, ignition_state, bms_soc2, odo, speed, gear, engine_rpm]

DimensionsMetric = namedtuple('DimensionsMetric', 'vin, trip_id')


# Function to get the randomvin
def rand_n(n):
    start = pow(10, n-1)
    end = pow(10, n) - 1
    return random.randint(start, end)


def random_vin():
    VIN = 'vin-' + str(rand_n(14))
    print(VIN)
    return VIN

def generateDimensions(scaleFactor):
    dimensionsMetrics = list()
    count = 0
    while count < scaleFactor*100000:
        count += 1
        trip_id = str(uuid.uuid4())
        vin = random_vin()
 
        # dimension data
        metric = DimensionsMetric(vin, trip_id)
        dimensionsMetrics.append(metric)

    return dimensionsMetrics


def create_record(measure_name, measure_value, value_type, timestamp, time_unit):
    return {
        "MeasureName": measure_name,
        "MeasureValue": str(measure_value),
        "MeasureValueType": value_type,
        "Time": str(timestamp),
        "TimeUnit": time_unit
    }



def createRandomMetrics(timestamp, timeUnit):
    records = list()

    records.append(create_record(systolic, random.randint(50, 80), "DOUBLE", timestamp, timeUnit))
    records.append(create_record(diastolic, random.randint(30, 50), "DOUBLE", timestamp, timeUnit))
    records.append(create_record(temp, random.randint(0, 1000), "DOUBLE", timestamp, timeUnit))
    records.append(create_record(pressureLevel, random.choice(['LOW', 'NORMAL', 'HIGH']), "VARCHAR", timestamp, timeUnit))

    

    for measure in remainingmetrics:
        value = 100.0 * random.random()
        records.append(create_record(measure, value, "DOUBLE", timestamp, timeUnit))

    return records



def send_records_to_kinesis(all_dimensions, kinesis_client, stream_name, sleep_time, percent_late, late_time):
    while True:
        if percent_late > 0:
            value = random.random()*100
            if (value >= percent_late):
                print("Generating On-Time Records.")
                local_timestamp = int(time.time())
            else:
                print("Generating Late Records.")
                local_timestamp = (int(time.time()) - late_time)
        else:
            local_timestamp = int(time.time())

        for series_id, dimensions in enumerate(all_dimensions):
            metrics = createRandomMetrics(local_timestamp, "SECONDS")

            dimensions = dimensions._asdict()  # convert named tuple to dict
            records = []
            for metric in metrics:
                metric.update(dimensions)  # adds the dimensions into metric dict
                data = json.dumps(metric)
                records.append({'Data': bytes(data, 'utf-8'), 'PartitionKey': metric['trip_id']})

            kinesis_client.put_records(StreamName=stream_name, Records=records)

            print("Wrote {} records to Kinesis Stream '{}'".format(len(metrics), stream_name))
        
        if sleep_time > 0:
            time.sleep(float(sleep_time)) 

def main(args):
    print(args)
    host_scale = args.hostScale  # scale factor for the hosts.

    dimension_measures = generateDimensions(host_scale)

    print("Dimensions for metrics: {}".format(len(dimension_measures)))

    def signal_handler(sig, frame):
        print("Exiting Application")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    stream_name = args.stream
    region_name = args.region
    kinesis_client = boto3.client('kinesis', region_name=region_name)

    sleep_time = args.sleep_time
    percent_late = args.percent_late
    late_time = args.late_time

    try:
        kinesis_client.describe_stream(StreamName=stream_name)
    except:
        print("Unable to describe Kinesis Stream '{}' in region {}".format(stream_name, region_name))
        sys.exit(0)

    send_records_to_kinesis(dimension_measures,
                            kinesis_client, stream_name, sleep_time, percent_late, late_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='timestream_kinesis_data_gen',
                                     description='DevOps Sample Data Generator for Timestream/KDA Sample Application.')

    parser.add_argument('--stream', action="store", type=str, default="TimestreamTestStream",
                        help="The name of Kinesis Stream.")
    parser.add_argument('--region', '-e', action="store", choices=['us-east-1', 'us-east-2', 'us-west-2', 'eu-west-1'],
                        default="us-east-1", help="Specify the region of the Kinesis Stream.")
    parser.add_argument('--host-scale', dest="hostScale", action="store", type=int, default=1,
                        help="The scale factor determines the number of hosts emitting events and metrics.")
    parser.add_argument('--profile', action="store", type=str, default=None, help="The AWS Config profile to use.")

    # Optional sleep timer to slow down data
    parser.add_argument('--sleep-time', action="store", type=int, default=0,
                        help="The amount of time in seconds to sleep between sending batches.")

    # Optional "Late" arriving data parameters
    parser.add_argument('--percent-late', action="store", type=float, default=0,
                        help="The percentage of data written that is late arriving ")
    parser.add_argument("--late-time", action="store", type=int, default=0,
                        help="The amount of time in seconds late that the data arrives")

    main(parser.parse_args())
