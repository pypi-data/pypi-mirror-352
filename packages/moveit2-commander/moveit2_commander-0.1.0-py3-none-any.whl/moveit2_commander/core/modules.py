# Python Standard Library
import os
import sys
import time
import json
from abc import ABC, abstractmethod
from typing import List

# Third-Party Libraries
import numpy as np

# ROS2 Core Libraries
import rclpy
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.task import Future
from rclpy.time import Time

# ROS2 Message Types
from builtin_interfaces.msg import Duration as BuiltinDuration
from control_msgs.action import GripperCommand
from geometry_msgs.msg import *
from moveit_msgs.action import ExecuteTrajectory
from moveit_msgs.msg import *
from moveit_msgs.srv import *
from nav_msgs.msg import *
from sensor_msgs.msg import *
from shape_msgs.msg import *
from std_msgs.msg import *
from trajectory_msgs.msg import *
from visualization_msgs.msg import *

# ROS2 TF Libraries
from tf2_ros import *


class Manager(object):
    def __init__(self, node: Node, *args, **kwargs):
        self._node = node
