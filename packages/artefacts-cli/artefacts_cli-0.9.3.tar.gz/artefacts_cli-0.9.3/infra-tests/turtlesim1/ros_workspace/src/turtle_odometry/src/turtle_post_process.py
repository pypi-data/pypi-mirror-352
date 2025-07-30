#!/usr/bin/env python3
#
# example command
# rosrun turtle_odometry turtle_post_process.py --bag_path /home/turtle/.ros/2022-09-07-15-09-50.bag --out_folder /home/turtle/.ros/test_results/turtle_odometry_postprocess


import rosbag
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import argparse
import sys

DEG2RAD = np.pi / 180.0

parser = argparse.ArgumentParser(description="turtle post processing")
parser.add_argument("--bag_path", help="path to input ROS bag")
parser.add_argument("--out_folder", help="folder path for outputs (e.g .html files)")
args = vars(parser.parse_args())

# choose topics to extract from rosbag
ROBOT = "turtle1"
estimated_topic = f"{ROBOT}/pose"
groundtruth_topic = f"{ROBOT}/odometry"

# make sure topics are in rosbag: adjust if needed, quit otherwise
topics = rosbag.Bag(args["bag_path"]).get_type_and_topic_info()[1].keys()


def adjust_topic(topic, topics):
    if topic not in topics:  # "try to add or remove the leading slash"
        if topic[0] == "/":
            topic = topic[1:]
        else:
            topic = "/" + topic
    if topic in topics:
        return topic
    else:
        print(
            f"[in post-process] topic {topic} not found in rosbag topic list {topics}. Exiting.."
        )
        sys.exit()


estimated_topic = adjust_topic(estimated_topic, topics)
groundtruth_topic = adjust_topic(groundtruth_topic, topics)

# preliminary check: make sure bag indexes are in increasing time order
with rosbag.Bag(args["bag_path"], "r") as bag:
    timelist = [msg.timestamp.to_sec() for msg in bag.read_messages()]
assert timelist == sorted(timelist)

# extract messages from rosbag
estimated_messages = []
groundtruth_messages = []
with rosbag.Bag(args["bag_path"], "r") as bag:
    estimated_messages = [_ for _ in bag.read_messages(topics=estimated_topic)]
    groundtruth_messages = [_ for _ in bag.read_messages(topics=groundtruth_topic)]


# helper functions
def compute_distance_travelled(message_list):
    """given a list of messages of TurtlePose type,
    compute the distance travelled between each timestamp
    return a list of dictionaries: timestamp and cummulated distance travelled
    """
    distance = 0
    distance_list = []
    prev_position = None
    for msg in message_list:
        if prev_position is None:
            prev_position = msg.message.x, msg.message.y
            distance_list.append({"timestamp": msg.timestamp, "cummulated_distance": 0})
        else:
            current_position = msg.message.x, msg.message.y
            distance += np.sqrt(
                (current_position[0] - prev_position[0]) ** 2
                + (current_position[1] - prev_position[1]) ** 2
            )
            distance_list.append(
                {"timestamp": msg.timestamp, "cummulated_distance": distance}
            )
            prev_position = current_position
    return distance_list


def match_lookup(lookup_time, lookup_list, previous_index, max_search=100):
    """finds the first message in lookup_list with a timestamp after lookup_time
    within previous_index and previous_index + max_search
    checks the previous message too. returns whichever is the closest to the lookup_time
    """
    assert len(lookup_list) > previous_index, (
        f"previous index = {previous_index} is beyond bounds of lookup list of length {len(lookup_list)}"
    )
    time_delta = -1  # initialize as negative
    i = previous_index
    while (
        time_delta < 0 and i < previous_index + max_search
    ):  # lookup_list time is before lookup_time
        time_delta = lookup_list[i].timestamp.to_sec() - lookup_time
        i += 1

        if i == previous_index + max_search:
            print(
                f"[info: post_process] index={i}: max_search exceeded, returning latest item of lookup_list. Check message frequencies"
            )
            return i - 1, lookup_list[i - 1]
        if i >= len(lookup_list):
            # print(f"[info: post_process] index={i}: no match found, returning last item of lookup_list")
            return i - 1, lookup_list[-1]

    # Check the previous message and return that one if the time delta is smaller
    if i - 2 > 0 and abs(lookup_list[i - 2].timestamp.to_sec() - lookup_time) < abs(
        time_delta
    ):
        return i - 2, lookup_list[i - 2]
    else:
        return i - 1, lookup_list[i - 1]


# basic metrics
def error_horiz(groundtruth_msg, estimated_msg):
    return np.sqrt(
        (groundtruth_msg.message.x - estimated_msg.message.x) ** 2
        + (groundtruth_msg.message.y - estimated_msg.message.y) ** 2
    )


def error_yaw(groundtruth_msg, estimated_msg):
    return np.abs(groundtruth_msg.message.theta - estimated_msg.message.theta)


# match messages via their timestamp
matched_messages = []
prev_index = 0
for msg in estimated_messages:
    prev_index, matched_msg = match_lookup(
        lookup_time=msg.timestamp.to_sec(),  # find the estimated message's timestamp
        lookup_list=groundtruth_messages,  # within the groundtruth messages
        previous_index=prev_index,  # (start looking at the previous match to make it fast!)
    )
    matched_messages.append({"estimated": msg, "groundtruth": matched_msg})
assert len(matched_messages) == len(estimated_messages)
N = 50
assert len(matched_messages) > N, (
    "[error in turtle_post_process] not enough matched messages found"
)
# remove garbage messages logged during test setup
# @TODO replace hard-coded assumption of N first messages with an event trigger
matched_messages = matched_messages[N:]


# plot time deltas between matched messages to verify correct match
time_deltas = [
    match["groundtruth"].timestamp.to_sec() - match["estimated"].timestamp.to_sec()
    for match in matched_messages
]
fig = px.scatter(
    time_deltas,
    title=f"Time delta for each matched pair of messages <br>Max time delta = {max([abs(t) for t in time_deltas]) * 1000:.0f} ms",
    labels={"value": "time delta (s)"},
)
fig.write_html(args["out_folder"] + "/mtime_deltas.html")

# plot metrics as a function of test time
start_time = matched_messages[0]["groundtruth"].timestamp.to_sec()
fig = px.scatter(
    x=[
        match["groundtruth"].timestamp.to_sec() - start_time
        for match in matched_messages
    ],
    y=[
        error_horiz(match["groundtruth"], match["estimated"])
        for match in matched_messages
    ],
    title=f"Horizontal error over time <br>Final error = {error_horiz(matched_messages[-1]['groundtruth'], matched_messages[-1]['estimated']):.2f} m",
    labels={"x": "time (s)", "y": "error (m)"},
)
fig.write_html(args["out_folder"] + "/error_horiz_time.html")

start_time = matched_messages[0]["groundtruth"].timestamp.to_sec()
fig = px.scatter(
    x=[
        match["groundtruth"].timestamp.to_sec() - start_time
        for match in matched_messages
    ],
    y=[
        error_yaw(match["groundtruth"], match["estimated"]) / DEG2RAD
        for match in matched_messages
    ],
    title=f"Yaw orientation error over time <br>Final error = {error_yaw(matched_messages[-1]['groundtruth'], matched_messages[-1]['estimated']) / DEG2RAD:.2f} deg",
    labels={"x": "time (s)", "y": "error (degrees)"},
    range_y=[-1, 10],
)
fig.write_html(args["out_folder"] + "/error_orientation_time.html")

# plot metrics as a function of distance travelled
distance_list = compute_distance_travelled(
    [match["groundtruth"] for match in matched_messages]
)
assert len(distance_list) == len(matched_messages)
total_distance = distance_list[-1]["cummulated_distance"]
start_time = distance_list[0]["timestamp"].to_sec()
fig = px.scatter(
    x=[_["timestamp"].to_sec() - start_time for _ in distance_list],
    y=[_["cummulated_distance"] for _ in distance_list],
    title=f"Distance travelled over time <br>Total distance = {total_distance:.1f} m",
    labels={"x": "timestamp (s)", "y": "cummulated distance (m)"},
)
fig.write_html(args["out_folder"] + "/distance_travelled.html")

fig = px.scatter(
    x=[_["cummulated_distance"] for _ in distance_list],
    y=[
        error_horiz(match["groundtruth"], match["estimated"])
        for match in matched_messages
    ],
    title=f"Horizontal error over distance travelled <br>Final error = {error_horiz(matched_messages[-1]['groundtruth'], matched_messages[-1]['estimated']):.2f} m",
    labels={"x": "distance travelled (m)", "y": "error (m)"},
)
fig.write_html(args["out_folder"] + "/error_horiz_distance.html")

fig = px.scatter(
    x=[_["cummulated_distance"] for _ in distance_list],
    y=[
        error_yaw(match["groundtruth"], match["estimated"]) / DEG2RAD
        for match in matched_messages
    ],
    title=f"Yaw orientation error over distance travelled <br>Final error = {error_yaw(matched_messages[-1]['groundtruth'], matched_messages[-1]['estimated']) / DEG2RAD:.2f} deg",
    labels={"x": "distance travelled (m)", "y": "error (degrees)"},
    range_y=[-1, 10],
)
fig.write_html(args["out_folder"] + "/error_orientation_distance.html")

# plot the trajectory (ground truth and estimated)
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=[match["groundtruth"].message.x for match in matched_messages],
        y=[match["groundtruth"].message.y for match in matched_messages],
        mode="lines+markers",
        name="groundtruth",
    )
)
fig.add_trace(
    go.Scatter(
        x=[match["estimated"].message.x for match in matched_messages],
        y=[match["estimated"].message.y for match in matched_messages],
        mode="lines+markers",
        name="estimated odometry",
    )
)
fig.update_layout(
    title="Turtle trajectory: ground truth vs estimated from odometry",
    xaxis_title="x",
    yaxis_title="y",
    margin_t=30,
    margin_b=0,
    margin_l=0,
    margin_r=0,
)
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)
fig.write_html(args["out_folder"] + "/_trajectory.html")
