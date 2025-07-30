#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, Point
from turtlesim.msg import Pose as TurtlePose
import numpy as np
import threading


class TurtleTrajectory:
    def __init__(self, name, start_pose) -> None:
        self.name = name
        self.start_pose = start_pose
        self.pub_velocity = rospy.Publisher(
            f"/{self.name}/cmd_vel", Twist, queue_size=1
        )
        self.velocity = Twist()
        self.sub_gt_pose = rospy.Subscriber(
            f"/{self.name}/pose", TurtlePose, self.callback_gt_pose
        )
        rospy.sleep(0.5)
        # setup a command publisher in the background to avoid ROS timing issues
        self.command_event = threading.Event()
        self.command_thread = threading.Thread(target=self.fixed_rate_commands)
        self.command_thread.start()

    def stop_commands(self):
        self.command_event.set()
        self.command_thread.join()
        print("stopped: command publisher")

    def fixed_rate_commands(self):
        """[thread method] Constantly publish commands in the background"""
        r = rospy.Rate(50)
        while not self.command_event.is_set() and not rospy.is_shutdown():
            try:
                self.pub_velocity.publish(self.velocity)
                r.sleep()
            except rospy.ROSInterruptException:
                pass

    def callback_gt_pose(self, msg):
        self.gt_pose = msg

    def closed_loop_square(self, speed=3.0, segment_length=10.0):
        # the turtlesim area is 11 by 11 meters
        # (0, 0) is bottom left / x horizontal to the right / y vertical to the top

        assert self.start_pose["theta"] == 0  # only supported
        assert self.start_pose["x"] + segment_length <= 11.0  # max size of turtlesim
        assert self.start_pose["y"] + segment_length <= 11.0  # max size of turtlesim

        try:
            r = rospy.Rate(
                70
            )  # match ground truth pose check rate with its publish rate

            # right
            self.velocity = Twist(linear=Point(x=speed))
            while self.gt_pose.x < segment_length + self.start_pose["x"]:
                r.sleep()
            # spot turn left
            self.velocity = Twist(angular=Point(z=speed / 3))
            while self.gt_pose.theta < np.pi / 2 and self.gt_pose.theta >= 0:
                r.sleep()

            # up
            self.velocity = Twist(linear=Point(x=speed))
            while self.gt_pose.y < segment_length + self.start_pose["y"]:
                r.sleep()
            # spot turn left
            self.velocity = Twist(angular=Point(z=speed / 3))
            while self.gt_pose.theta < np.pi and self.gt_pose.theta >= 0:
                r.sleep()

            # left
            self.velocity = Twist(linear=Point(x=speed))
            while self.gt_pose.x > self.start_pose["x"]:
                r.sleep()
            # spot turn left
            self.velocity = Twist(angular=Point(z=speed / 3))
            while self.gt_pose.theta < -np.pi / 2 and self.gt_pose.theta <= 0:
                r.sleep()

            # down
            self.velocity = Twist(linear=Point(x=speed))
            while self.gt_pose.y > self.start_pose["y"]:
                r.sleep()
            self.velocity = Twist()  # stop
            rospy.sleep(0.1)

        except (KeyboardInterrupt, rospy.ROSInterruptException):
            self.stop_commands()


def main():
    NAME = "turtle1"
    rospy.init_node("turtle_trajectory")
    try:
        # setup turtlesim
        from turtlesim.srv import TeleportAbsolute

        rospy.wait_for_service(f"/{NAME}/teleport_absolute")
        srv_teleport_absolute = rospy.ServiceProxy(
            f"/{NAME}/teleport_absolute", TeleportAbsolute
        )
        start_pose = {"x": 1, "y": 1, "theta": 0}
        srv_teleport_absolute(
            x=start_pose["x"], y=start_pose["y"], theta=start_pose["theta"]
        )

        # run the trajectory
        tj = TurtleTrajectory(NAME, start_pose)
        rospy.loginfo("starting turtle trajectory")
        tj.closed_loop_square(speed=5.0, segment_length=5.0)
        tj.stop_commands()  # to stop publisher
        rospy.sleep(1)
        # rospy.spin()      # to keep script running
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
