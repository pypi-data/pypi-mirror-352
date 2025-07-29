from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class KinematicPath_ServiceManager(ServiceManager):
    def __init__(
        self, node: Node, planning_group: str = "ur_manipulator", *args, **kwargs
    ):
        """
        ServiceManager for the MoveIt2 Kinematic Path service.
        This class is responsible for managing the service that computes a kinematic path
        for a robot based on the provided goal constraints and joint states.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - planning_group (str): The name of the planning group for which to compute the kinematic path.
          Defaults to "ur_manipulator".
        - *args, **kwargs: Additional arguments for future extensibility.

        Static Method:
        - get_goal_constraint: A static method to create a goal constraint from a JointState instance.
          It takes the desired joint states and an optional tolerance value, returning a Constraints object.
        """
        super().__init__(
            node,
            service_name="/plan_kinematic_path",
            service_type=GetMotionPlan,
            *args,
            **kwargs,
        )

        self._planning_group = planning_group

    def run(
        self,
        goal_constraints: List[Constraints],
        path_constraints: Constraints,
        joint_states: JointState,
        num_planning_attempts: int = 100,
        allowed_planning_time: float = 1.0,
        max_velocity_scaling_factor: float = 1.0,
        max_acceleration_scaling_factor: float = 1.0,
    ) -> RobotTrajectory:
        """
        Method to compute a kinematic path for the robot based on the provided goal constraints and joint states.

        Parameters:
        - goal_constraints (List[Constraints]): A list of Constraints objects that define the goal constraints for the kinematic path.
        - path_constraints (Constraints): Constraints that define the path constraints for the kinematic path. None is allowed.
        - joint_states (JointState): The current joint states of the robot. This variable must be provided.

        - Planning Parameters:
            - num_planning_attempts (int): The number of planning attempts to make. Defaults to 100.
            - allowed_planning_time (float): The maximum time allowed for planning in seconds. Defaults to 1.0.
            - max_velocity_scaling_factor (float): The maximum velocity scaling factor for the planning. Defaults to 1.0.
            - max_acceleration_scaling_factor (float): The maximum acceleration scaling factor for the planning. Defaults to 1.0.

        Returns:
        - RobotTrajectory: The computed kinematic path as a RobotTrajectory instance.

        Raises:
        - AssertionError: If joint_states is not an instance of JointState or goal_constraints is not a list of Constraints instances.
        - None: If the service call fails or the error code is not SUCCESS.
        """
        assert isinstance(
            joint_states, JointState
        ), "joint_states must be a JointState instance."
        assert isinstance(
            goal_constraints, list
        ), "goal_constraints must be a list of Constraints instances."
        assert all(
            isinstance(constraint, Constraints) for constraint in goal_constraints
        ), "All items in goal_constraints must be Constraints instances."

        # Unused Parameters:
        #     - workspace_parameters
        #     - path_constraints
        #     - trajectory_constraints
        #     - reference_trajectories
        #     - pipeline_id
        #     - planner_id

        request = GetMotionPlan.Request(
            motion_plan_request=MotionPlanRequest(
                start_state=RobotState(joint_state=joint_states),
                goal_constraints=goal_constraints,
                group_name=self._planning_group,
                num_planning_attempts=num_planning_attempts,
                allowed_planning_time=allowed_planning_time,
                max_velocity_scaling_factor=max_velocity_scaling_factor,
                max_acceleration_scaling_factor=max_acceleration_scaling_factor,
            )
        )

        if path_constraints is not None:
            request.motion_plan_request.path_constraints = path_constraints

        response: GetMotionPlan.Response = self._send_request(request)
        trajectory: RobotTrajectory = self._handle_response(response)

        return trajectory

    def _handle_response(
        self,
        response: GetMotionPlan.Response,
    ) -> RobotTrajectory:
        """
        Method to handle the response from the Kinematic Path service.

        Parameters:
        - response (GetMotionPlan.Response): The response from the Kinematic Path service.

        Returns:
        - RobotTrajectory: The computed kinematic path as a RobotTrajectory instance, or None if the service call failed.

        Raises:
        - None: If the service call fails or the error code is not SUCCESS.
        """

        response_msg: MotionPlanResponse = response.motion_plan_response

        code = response_msg.error_code.val
        if code != MoveItErrorCodes.SUCCESS:
            code_type = self._get_error_code(code)
            self._node.get_logger().warn(
                f"Error code in plan_kinematic_path service: {code}/{code_type}"
            )
            return None

        trajectory: RobotTrajectory = response_msg.trajectory

        return trajectory

    @staticmethod
    def get_goal_constraint(
        goal_joint_states: JointState,
        tolerance: float = 0.05,
    ):
        """
        Static method to create a goal constraint from a JointState instance.

        Parameters:
        - goal_joint_states (JointState): The desired joint states for the goal constraint. This variable must be provided.
        - tolerance (float): The tolerance for the joint positions. Defaults to 0.05. If None, no tolerance is applied.

        Returns:
        - Constraints: A Constraints object containing the goal constraints for the kinematic path.
        """
        assert isinstance(
            goal_joint_states, JointState
        ), "goal_joint_states must be a JointState instance."

        name, position = goal_joint_states.name, goal_joint_states.position

        joint_constraints = []
        for n, p in zip(name, position):
            joint_constraint = JointConstraint(
                joint_name=n,
                position=p,
                weight=0.1,
            )

            if tolerance is not None:
                joint_constraint.tolerance_above = tolerance
                joint_constraint.tolerance_below = tolerance

            joint_constraints.append(joint_constraint)

        constraints = Constraints(
            name="goal_constraints",
            joint_constraints=joint_constraints,
        )

        return constraints
