#!/usr/bin/env python3
import sys
import unittest
from std_srvs.srv import Empty as EmptySrv
from turtlesim.srv import TeleportAbsolute, SetPen
from turtlesim.msg import Pose as TurtlePose
import rospy
import numpy as np
from turtle_trajectory import TurtleTrajectory

PKG = "turtle_odometry"
NAME = "turtle1"
# start_pose = {'x': 1, 'y': 1, 'theta': 0}


class TestTurtle(unittest.TestCase):
    # runs before each test_* method
    def setUp(self):
        ## Arange
        rospy.init_node("testurtle", anonymous=True)
        # setup the turtlesim simulator
        rospy.wait_for_service(f"/{NAME}/teleport_absolute")
        rospy.wait_for_service(f"/{NAME}/set_pen")
        rospy.wait_for_service("/clear")
        self.srv_teleport_absolute = rospy.ServiceProxy(
            f"/{NAME}/teleport_absolute", TeleportAbsolute
        )
        self.srv_set_pen = rospy.ServiceProxy(f"/{NAME}/set_pen", SetPen)
        self.srv_clear = rospy.ServiceProxy("/clear", EmptySrv)
        self.srv_set_pen(r=255, g=255, b=255, width=5, off=False)
        while not rospy.has_param("test/start_pose"):
            rospy.sleep(0.1)
        while not rospy.has_param("test/segment_length"):
            rospy.sleep(0.1)
        start_pose = rospy.get_param("test/start_pose", [1, 1, 0])
        self.segment_length = rospy.get_param("test/segment_length", 5.0)
        self.start_pose = dict(zip(["x", "y", "theta"], start_pose))
        self.srv_teleport_absolute(
            x=self.start_pose["x"],
            y=self.start_pose["y"],
            theta=self.start_pose["theta"],
        )
        self.srv_clear()
        # prepare trajectory commands for the test
        self.turtle_trajectory = TurtleTrajectory(NAME, self.start_pose)
        rospy.loginfo("setting up turtle trajectory")
        # init odometry to match the pose of the test setup
        rospy.wait_for_service(f"/{NAME}/odom_reset")
        self.srv_reset_odom = rospy.ServiceProxy(f"/{NAME}/odom_reset", EmptySrv)
        self.srv_reset_odom()

    def test_turtle(self):
        ## Act
        rospy.sleep(2)  # log some data while not moving
        self.turtle_trajectory.closed_loop_square(
            speed=5.0, segment_length=self.segment_length
        )  # drive the turtle!
        self.turtle_trajectory.stop_commands()
        rospy.sleep(1)  # log some data after stopped moving

        ## Assert
        final_pose = rospy.wait_for_message(f"/{NAME}/pose", TurtlePose, timeout=None)
        distance_to_start = np.sqrt(
            (final_pose.x - self.start_pose["x"]) ** 2
            + (final_pose.y - self.start_pose["y"]) ** 2
        )
        rospy.loginfo(f"distance to start: {distance_to_start}")
        # check if the turtle moved (= is not at exactly the starting position)
        self.assertNotEqual(
            distance_to_start,
            0,
            msg="turtle position at end of test exactly at starting position: did not move?",
        )
        # check if the turtle finished the loop trajectory
        self.assertAlmostEqual(
            distance_to_start,
            0,
            delta=0.5,
            msg=f"turtle position at end of test = {distance_to_start}m is more than 0.5m away from starting position: error in trajectory?",
        )


if __name__ == "__main__":
    import rostest

    rostest.rosrun(PKG, NAME, TestTurtle, sys.argv)
