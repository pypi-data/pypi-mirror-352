from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class FK_ServiceManager(ServiceManager):
    def __init__(self, node: Node, *args, **kwargs):
        """
        ServiceManager for the MoveIt2 Forward Kinematics (FK) service.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - *args, **kwargs: Additional arguments for future extensibility.
        """
        super().__init__(
            node,
            service_name="/compute_fk",
            service_type=GetPositionFK,
            *args,
            **kwargs,
        )

    def run(
        self, joint_states: JointState, end_effector: str = "wrist_3_link"
    ) -> PoseStamped:
        """
        Method to compute the forward kinematics for a given end effector.

        Parameters:
        - joint_states (JointState): The joint states of the robot. This variable must be provided.
        - end_effector (str): The name of the end effector link for which to compute FK.

        Returns:
        - PoseStamped: The pose of the end effector in the base_link frame.

        Raises:
        - AssertionError: If joint_states is not an instance of JointState.
        - None: If the service call fails or the error code is not SUCCESS.
        """

        assert isinstance(
            joint_states, JointState
        ), "joint_states must be a JointState instance."

        request = GetPositionFK.Request(
            header=Header(
                stamp=self._node.get_clock().now().to_msg(),
                frame_id="base_link",
            ),
            fk_link_names=[end_effector],
            robot_state=(RobotState(joint_state=joint_states)),
        )

        response: GetPositionFK.Response = self._send_request(request)
        result = self._handle_response(response)

        return result

    def _handle_response(self, response: GetPositionFK.Response) -> PoseStamped:
        """
        Handle the response from the FK service.

        Parameters:
        - response (GetPositionFK.Response): The response from the FK service.

        Returns:
        - PoseStamped: The pose of the end effector in the base_link frame.

        Raises:
        - None: If the service call was successful, returns the pose of the end effector.
        """

        code = response.error_code.val

        if code != MoveItErrorCodes.SUCCESS:
            code_type = self._get_error_code(code)
            self._node.get_logger().warn(
                f"Error code in compute_fk service: {code}/{code_type}"
            )
            return None

        pose_stamped: PoseStamped = response.pose_stamped[0]
        return pose_stamped
