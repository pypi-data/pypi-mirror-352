from moveit2_commander.core.modules import *


class ServiceManager(object):
    def __init__(
        self, node: Node, service_name: str, service_type: type, *args, **kwargs
    ):
        """
        Parent class for managing MoveIt2 services.

        Parameters:
        - node (Node): The ROS2 Node instance.
        - service_name (str): The name of the service to be managed.
        - service_type (type): The type of the service (e.g., MoveGroup, PlanningScene).
        - *args, **kwargs: Additional arguments for future extensibility.
        """
        self._node = node

        self._error_code = {
            "NOT_INITIALIZED": 0,
            "SUCCESS": 1,
            "FAILURE": 99999,
            "PLANNING_FAILED": -1,
            "INVALID_MOTION_PLAN": -2,
            "MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE": -3,
            "CONTROL_FAILED": -4,
            "UNABLE_TO_AQUIRE_SENSOR_DATA": -5,
            "TIMED_OUT": -6,
            "PREEMPTED": -7,
            "START_STATE_IN_COLLISION": -10,
            "START_STATE_VIOLATES_PATH_CONSTRAINTS": -11,
            "START_STATE_INVALID": -26,
            "GOAL_IN_COLLISION": -12,
            "GOAL_VIOLATES_PATH_CONSTRAINTS": -13,
            "GOAL_CONSTRAINTS_VIOLATED": -14,
            "GOAL_STATE_INVALID": -27,
            "UNRECOGNIZED_GOAL_TYPE": -28,
            "INVALID_GROUP_NAME": -15,
            "INVALID_GOAL_CONSTRAINTS": -16,
            "INVALID_ROBOT_STATE": -17,
            "INVALID_LINK_NAME": -18,
            "INVALID_OBJECT_NAME": -19,
            "FRAME_TRANSFORM_FAILURE": -21,
            "COLLISION_CHECKING_UNAVAILABLE": -22,
            "ROBOT_STATE_STALE": -23,
            "SENSOR_INFO_STALE": -24,
            "COMMUNICATION_FAILURE": -25,
            "CRASH": -29,
            "ABORT": -30,
            "NO_IK_SOLUTION": -31,
        }

        # >>> Service Parameters >>>
        self._service_name = service_name
        self._service_type = service_type
        # <<< Service Parameters <<<

        # >>> Service Client >>>
        self._srv = self._node.create_client(service_type, service_name)

        while not self._srv.wait_for_service(timeout_sec=1.0):
            self._node.get_logger().info(
                f"Service {service_name} not available, waiting again..."
            )
        # <<< Service Client <<<

    def _get_error_code(self, code: int):
        for key, value in self._error_code.items():
            if value == code:
                return key

        return "UNKNOWN"

    def _send_request(self, request):
        res = self._srv.call(request)
        return res

    @abstractmethod
    def run(self):
        """
        Method to run the service.
        This method should be implemented in the subclass to define
        the specific behavior of the service.
        """
        raise NotImplementedError("run must be implemented in the subclass")

    @abstractmethod
    def _handle_response(self):
        """
        Method to handle the response from the service call.
        This method should be implemented in the subclass to define
        how to process the response from the service.
        """
        raise NotImplementedError(
            "_handle_response must be implemented in the subclass"
        )
