from moveit2_commander.core.modules import *
from moveit2_commander.core.service_manager import ServiceManager


class ApplyPlanningScene_ServiceManager(ServiceManager):
    """
    ServiceManager for the MoveIt2 Apply Planning Scene service.
    This class is responsible for managing the service that applies changes to the planning scene
    in the MoveIt2 system.

    Parameters:
    - node (Node): The ROS2 Node instance.
    - *args, **kwargs: Additional arguments for future extensibility.
    """

    def __init__(self, node: Node, *args, **kwargs):
        super().__init__(
            node,
            service_name="/apply_planning_scene",
            service_type=ApplyPlanningScene,
            *args,
            **kwargs,
        )

    def run(
        self, collision_objects: List[CollisionObject], scene: PlanningScene
    ) -> bool:
        """
        Method to apply a planning scene with the provided collision objects.

        Parameters:
        - collision_objects (List[CollisionObject]): A list of CollisionObject instances to be added to the planning scene.
        - scene (PlanningScene): The PlanningScene instance to which the collision objects will be applied.

        Returns:
        - bool: True if the planning scene was successfully applied, False otherwise.

        Raises:
        - AssertionError: If scene is not an instance of PlanningScene or collision_objects is not a list of CollisionObject instances.
        """

        assert isinstance(
            scene, PlanningScene
        ), "scene must be a PlanningScene instance."
        assert isinstance(
            collision_objects, list
        ), "collision_objects must be a list of CollisionObject instances."
        assert all(
            isinstance(obj, CollisionObject) for obj in collision_objects
        ), "All items in collision_objects must be CollisionObject instances."

        scene.world.collision_objects = collision_objects

        request = ApplyPlanningScene.Request(scene=scene)
        response: ApplyPlanningScene.Response = self._send_request(request)

        result = self._handle_response(response)

        return result

    def _handle_response(self, response: ApplyPlanningScene.Response) -> bool:
        success: bool = response.success
        return success
