from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class CartesianPath_ServiceManager(ServiceManager):
    def __init__(
        self,
        node: Node,
        planning_group: str = "ur_manipulator",
        fraction_threshold: float = 0.999,
        *args,
        **kwargs,
    ):
        """
        ServiceManager for the MoveIt2 Cartesian Path service.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - planning_group (str): The name of the planning group for which to compute the Cartesian path.
        - fraction_threshold (float): The minimum fraction of the path that must be valid for the service to succeed.
          Defaults to 0.999. If the fraction of the path is below this threshold, the service will return False.
        - *args, **kwargs: Additional arguments for future extensibility.
        """
        super().__init__(
            node,
            service_name="/compute_cartesian_path",
            service_type=GetCartesianPath,
            *args,
            **kwargs,
        )

        self._planning_group = planning_group
        self._fraction_threshold = fraction_threshold

    def run(
        self,
        header: Header,
        waypoints: List[Pose],
        joint_states: JointState,
        end_effector: str = "wrist_3_link",
    ) -> RobotTrajectory:
        """
        Method to compute the Cartesian path for a given set of waypoints and joint states.

        Parameters:
        - header (Header): The header for the request, typically containing the timestamp and frame_id.
        - waypoints (List[Pose]): A list of Pose instances representing the waypoints for the Cartesian path.
        - joint_states (JointState): The current joint states of the robot. This variable must be provided.
        - end_effector (str): The name of the end effector link for which to compute the Cartesian path.

        Returns:
        - RobotTrajectory: The computed Cartesian path as a RobotTrajectory instance.

        Raises:
        - AssertionError: If header is not an instance of Header, waypoints is not a list of Pose instances,
          or joint_states is not an instance of JointState.
        - None: If the service call fails or the error code is not SUCCESS.
        """
        assert isinstance(header, Header), "header must be a Header instance."
        assert isinstance(
            waypoints, list
        ), "waypoints must be a list of Pose instances."
        assert all(
            isinstance(waypoint, Pose) for waypoint in waypoints
        ), "All items in waypoints must be Pose instances."
        assert isinstance(
            joint_states, JointState
        ), "joint_states must be a JointState instance."

        request = GetCartesianPath.Request(
            header=header,
            start_state=RobotState(joint_state=joint_states),
            group_name=self._planning_group,
            link_name=end_effector,
            waypoints=waypoints,
            max_step=0.05,
            jump_threshold=5.0,
            avoid_collisions=True,
        )

        response: GetCartesianPath.Response = self._send_request(request)
        result = self._handle_response(response)

        return result

    def _handle_response(
        self,
        response: GetCartesianPath.Response,
    ) -> RobotTrajectory:
        """
        Method to handle the response from the Cartesian path service.

        Parameters:
        - response (GetCartesianPath.Response): The response from the Cartesian path service.

        Returns:
        - RobotTrajectory: The computed Cartesian path as a RobotTrajectory instance, or None if the service call failed.

        Raises:
        - None: If the service call fails or the error code is not SUCCESS.
        """
        code = response.error_code.val

        if code != MoveItErrorCodes.SUCCESS:
            code_type = self._get_error_code(code)
            self._node.get_logger().warn(
                f"Error code in compute_cartesian_path service: {code}/{code_type}"
            )
            return None

        trajectory: RobotTrajectory = response.solution
        fraction = response.fraction

        if fraction < self._fraction_threshold:
            self._node.get_logger().warn(
                f"Fraction is under {self._fraction_threshold}: {fraction}"
            )
            return None

        return trajectory
