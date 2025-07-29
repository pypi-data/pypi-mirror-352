from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class GetPlanningScene_ServiceManager(ServiceManager):
    """
    ServiceManager for the MoveIt2 Get Planning Scene service.
    This class is responsible for managing the service that retrieves the current planning scene
    from the MoveIt2 system.

    Parameters:
    - node (Node): The ROS2 Node instance.
    - *args, **kwargs: Additional arguments for future extensibility.
    """

    def __init__(self, node: Node, *args, **kwargs):
        super().__init__(
            node,
            service_name="/get_planning_scene",
            service_type=GetPlanningScene,
            *args,
            **kwargs,
        )

    def run(self) -> PlanningScene:
        """
        Method to retrieve the current planning scene from the MoveIt2 system.

        Returns:
        - PlanningScene: The current planning scene, which includes information about the robot's state,
          the environment, and any obstacles.
        """

        request = GetPlanningScene.Request()
        response: GetPlanningScene.Response = self._send_request(request)

        scene = self._handle_response(response)

        return scene

    def _handle_response(self, response: GetPlanningScene.Response) -> PlanningScene:
        scene: PlanningScene = response.scene
        return scene
