=================
moveit2_commander
=================


.. image:: https://img.shields.io/pypi/v/moveit2_commander.svg
        :target: https://pypi.python.org/pypi/moveit2_commander

.. image:: https://img.shields.io/travis/SoYu/moveit2_commander.svg
        :target: https://travis-ci.com/SoYu/moveit2_commander

.. image:: https://readthedocs.org/projects/moveit2-commander/badge/?version=latest
        :target: https://moveit2-commander.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




package for controlling moveit2 services


* Free software: MIT license
* Documentation: https://moveit2-commander.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


## Requirements

This package depends on ROS2 packages and message types:

- ROS2 Core Libraries:
        - rclpy
        - rclpy.action.ActionClient
        - rclpy.action.client.ClientGoalHandle
        - rclpy.duration.Duration
        - rclpy.node.Node
        - rclpy.qos.QoSProfile
        - rclpy.qos.qos_profile_system_default
        - rclpy.task.Future
        - rclpy.time.Time

- ROS2 Message Types:
        - builtin_interfaces.msg.Duration
        - control_msgs.action.GripperCommand
        - geometry_msgs.msg.*
        - moveit_msgs.action.ExecuteTrajectory
        - moveit_msgs.msg.*
        - moveit_msgs.srv.*
        - nav_msgs.msg.*
        - sensor_msgs.msg.*
        - shape_msgs.msg.*
        - std_msgs.msg.*
        - trajectory_msgs.msg.*
        - visualization_msgs.msg.*