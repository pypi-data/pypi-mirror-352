from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class ExecuteTrajectory_ServiceManager(Manager):
    def __init__(self, node: Node, *args, **kwargs):
        """
        ServiceManager for the MoveIt2 Execute Trajectory service.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - *args, **kwargs: Additional arguments for future extensibility.

        Static Method:
        - scale_trajectory(trajectory: RobotTrajectory, scale_factor: float) -> RobotTrajectory:
          Scales the duration and velocities of the trajectory by a given factor.
          This method is static and can be called without an instance of the class.
        """

        super().__init__(
            node,
            *args,
            **kwargs,
        )

        self._action_client = ActionClient(
            self._node, ExecuteTrajectory, "/execute_trajectory"
        )

    def run(self, trajectory: RobotTrajectory) -> ExecuteTrajectory.Result:
        """
        Method to execute a trajectory using the MoveIt2 Execute Trajectory service.

        Parameters:
        - trajectory (RobotTrajectory): The trajectory to be executed. This variable must be provided.

        Returns:
        - ExecuteTrajectory.Result: The result of the trajectory execution, which includes the status and any feedback.
        """
        goal_msg = ExecuteTrajectory.Goal(trajectory=trajectory)
        self._action_client.wait_for_server()

        response: ExecuteTrajectory.Result = self._action_client.send_goal(
            goal_msg, feedback_callback=self._feedback_callback
        )
        return response

    def _feedback_callback(self, feedback_msg: ExecuteTrajectory.Feedback):
        # self._node.get_logger().info(f"Received feedback: {feedback_msg}")
        pass

    @staticmethod
    def scale_trajectory(
        trajectory: RobotTrajectory, scale_factor: float
    ) -> RobotTrajectory:
        """
        Method to scale the duration and velocities of a trajectory by a given factor.
        """

        def scale_duration(duration: BuiltinDuration, factor: float) -> BuiltinDuration:
            # 전체 시간을 나노초로 환산
            total_nanosec = duration.sec * 1_000_000_000 + duration.nanosec
            # n배
            scaled_nanosec = int(total_nanosec * factor)

            # 다시 sec과 nanosec으로 분리
            new_sec = scaled_nanosec // 1_000_000_000
            new_nanosec = scaled_nanosec % 1_000_000_000

            return BuiltinDuration(sec=new_sec, nanosec=new_nanosec)

        new_points = []
        for point in trajectory.joint_trajectory.points:
            point: JointTrajectoryPoint

            new_point = JointTrajectoryPoint(
                positions=np.array(point.positions),
                velocities=np.array(point.velocities) * scale_factor,
                accelerations=np.array(point.accelerations) * scale_factor,
                time_from_start=scale_duration(
                    duration=point.time_from_start, factor=(1.0 / scale_factor)
                ),
            )
            new_points.append(new_point)

        new_joint_trajectory = JointTrajectory(
            header=trajectory.joint_trajectory.header,
            joint_names=trajectory.joint_trajectory.joint_names,
            points=new_points,
        )

        new_trajectory = RobotTrajectory(
            joint_trajectory=new_joint_trajectory,
            multi_dof_joint_trajectory=trajectory.multi_dof_joint_trajectory,
        )

        return new_trajectory
