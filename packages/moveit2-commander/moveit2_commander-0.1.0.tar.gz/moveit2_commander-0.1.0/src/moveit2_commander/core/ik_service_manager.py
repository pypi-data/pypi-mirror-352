from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class IK_ServiceManager(ServiceManager):
    def __init__(self, node: Node, *args, **kwargs):
        """
        ServiceManager for the MoveIt2 Inverse Kinematics (IK) service.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - *args, **kwargs: Additional arguments for future extensibility.
        """
        super().__init__(
            node,
            service_name="/compute_ik",
            service_type=GetPositionIK,
            *args,
            **kwargs,
        )

    def run(
        self,
        pose_stamped: PoseStamped,
        joint_states: JointState,
        end_effector: str = "wrist_3_link",
        avoid_collisions: bool = False,
    ) -> RobotState:
        """
        Method to compute the inverse kinematics for a given pose and joint states.

        Parameters:
        - pose_stamped (PoseStamped): The desired pose of the end effector in the base_link frame.
        - joint_states (JointState): The current joint states of the robot. This variable must be provided.
        - end_effector (str): The name of the end effector link for which to compute IK.
        - avoid_collisions (bool): Whether to avoid collisions during the IK computation. Defaults to False.

        Returns:
        - RobotState: The joint states that achieve the desired pose of the end effector.

        Raises:
        - AssertionError: If joint_states is not an instance of JointState or pose_stamped is not an instance of PoseStamped.
        - None: If the service call fails or the error code is not SUCCESS.

        """
        assert isinstance(
            joint_states, JointState
        ), "joint_states must be a JointState instance."
        assert isinstance(
            pose_stamped, PoseStamped
        ), "pose_stamped must be a PoseStamped instance."

        if joint_states is None or pose_stamped is None:
            raise ValueError("joint_states and pose_stamped must be provided.")

        request = GetPositionIK.Request(
            ik_request=PositionIKRequest(
                group_name="ur_manipulator",
                robot_state=RobotState(joint_state=joint_states),
                avoid_collisions=avoid_collisions,
                ik_link_name=end_effector,
                pose_stamped=pose_stamped,
            )
        )

        response: GetPositionIK.Response = self._send_request(request)
        result = self._handle_response(response)

        return result

    def _handle_response(self, response: GetPositionIK.Response) -> RobotState:
        """
        Handle the response from the IK service.

        Parameters:
        - response (GetPositionIK.Response): The response from the IK service.

        Returns:
        - RobotState: The joint states that achieve the desired pose of the end effector.

        Raises:
        - None: If the service call was successful, returns the joint states.
        """

        code = response.error_code.val

        if code != MoveItErrorCodes.SUCCESS:
            code_type = self._get_error_code(code)
            self._node.get_logger().warn(
                f"Error code in compute_ik service: {code}/{code_type}"
            )
            return None

        solution: RobotState = response.solution

        return solution
