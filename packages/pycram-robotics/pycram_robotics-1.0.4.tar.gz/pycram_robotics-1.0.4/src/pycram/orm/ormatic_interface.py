from pycram.orm.casts import StringType

from ormatic.custom_types import TypeType
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import RelationshipProperty, registry, relationship
import pycram.datastructures.dataclasses
import pycram.datastructures.grasp
import pycram.datastructures.pose
import pycram.designator
import pycram.designators.action_designator
import pycram.language
import pycram.orm.model
import pycram.plan

metadata = MetaData()


t_GraspDescription = Table(
    'GraspDescription', metadata,
    Column('id', Integer, primary_key=True),
    Column('approach_direction', Enum(pycram.datastructures.enums.Grasp), nullable=False),
    Column('vertical_alignment', Enum(pycram.datastructures.enums.Grasp)),
    Column('rotate_gripper', Boolean, nullable=False)
)

t_Header = Table(
    'Header', metadata,
    Column('id', Integer, primary_key=True),
    Column('frame_id', String, nullable=False),
    Column('stamp', DateTime, nullable=False),
    Column('sequence', Integer, nullable=False)
)

t_ORMActionNode = Table(
    'ORMActionNode', metadata,
    Column('id', Integer, primary_key=True)
)

t_ORMMotionNode = Table(
    'ORMMotionNode', metadata,
    Column('id', Integer, primary_key=True)
)

t_PlanNode = Table(
    'PlanNode', metadata,
    Column('id', Integer, primary_key=True),
    Column('status', Enum(pycram.datastructures.enums.TaskStatus), nullable=False),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('polymorphic_type', String)
)

t_Quaternion = Table(
    'Quaternion', metadata,
    Column('id', Integer, primary_key=True),
    Column('x', Float, nullable=False),
    Column('y', Float, nullable=False),
    Column('z', Float, nullable=False),
    Column('w', Float, nullable=False)
)

t_Vector3 = Table(
    'Vector3', metadata,
    Column('id', Integer, primary_key=True),
    Column('x', Float, nullable=False),
    Column('y', Float, nullable=False),
    Column('z', Float, nullable=False)
)

t_Pose = Table(
    'Pose', metadata,
    Column('id', Integer, primary_key=True),
    Column('position_id', ForeignKey('Vector3.id'), nullable=False),
    Column('orientation_id', ForeignKey('Quaternion.id'), nullable=False),
    Column('polymorphic_type', String)
)

t_PoseStamped = Table(
    'PoseStamped', metadata,
    Column('id', Integer, primary_key=True),
    Column('pose_id', ForeignKey('Pose.id'), nullable=False),
    Column('header_id', ForeignKey('Header.id'), nullable=False),
    Column('polymorphic_type', String)
)

t_Transform = Table(
    'Transform', metadata,
    Column('id', ForeignKey('Pose.id'), primary_key=True)
)

t_ActionDescription = Table(
    'ActionDescription', metadata,
    Column('id', Integer, primary_key=True),
    Column('robot_position_id', ForeignKey('PoseStamped.id')),
    Column('robot_torso_height', Float),
    Column('polymorphic_type', String)
)

t_FrozenObject = Table(
    'FrozenObject', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('concept', StringType, nullable=False),
    Column('pose_id', ForeignKey('PoseStamped.id'))
)

t_GraspPose = Table(
    'GraspPose', metadata,
    Column('id', ForeignKey('PoseStamped.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('grasp_description_id', ForeignKey('GraspDescription.id'), nullable=False)
)

t_TransformStamped = Table(
    'TransformStamped', metadata,
    Column('id', ForeignKey('PoseStamped.id'), primary_key=True),
    Column('pose_id', ForeignKey('Transform.id'), nullable=False),
    Column('child_frame_id', String, nullable=False)
)

t_CloseAction = Table(
    'CloseAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('grasping_prepose_distance', Float, nullable=False)
)

t_DetectAction = Table(
    'DetectAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('technique', Enum(pycram.datastructures.enums.DetectionTechnique), nullable=False),
    Column('state', Enum(pycram.datastructures.enums.DetectionState)),
    Column('region', String),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_FaceAtAction = Table(
    'FaceAtAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('pose_id', ForeignKey('PoseStamped.id'), nullable=False),
    Column('keep_joint_states', Boolean, nullable=False)
)

t_GraspingAction = Table(
    'GraspingAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'), nullable=False)
)

t_GripAction = Table(
    'GripAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('gripper', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('effort', Float, nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_LanguageNode = Table(
    'LanguageNode', metadata,
    Column('id', ForeignKey('PlanNode.id'), primary_key=True),
    Column('action_id', ForeignKey('ActionDescription.id'), nullable=False)
)

t_LookAtAction = Table(
    'LookAtAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('target_id', ForeignKey('PoseStamped.id'), nullable=False)
)

t_MoveTorsoAction = Table(
    'MoveTorsoAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('torso_state', Enum(pycram.datastructures.enums.TorsoState), nullable=False)
)

t_NavigateAction = Table(
    'NavigateAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('target_location_id', ForeignKey('PoseStamped.id'), nullable=False),
    Column('keep_joint_states', Boolean, nullable=False)
)

t_ORMResolvedActionNode = Table(
    'ORMResolvedActionNode', metadata,
    Column('id', Integer, primary_key=True),
    Column('designator_ref_id', ForeignKey('ActionDescription.id'), nullable=False)
)

t_OpenAction = Table(
    'OpenAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('grasping_prepose_distance', Float, nullable=False)
)

t_ParkArmsAction = Table(
    'ParkArmsAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False)
)

t_PickUpAction = Table(
    'PickUpAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_PlaceAction = Table(
    'PlaceAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('target_location_id', ForeignKey('PoseStamped.id'), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_ReachToPickUpAction = Table(
    'ReachToPickUpAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('grasp_description_id', ForeignKey('GraspDescription.id'), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_ReleaseAction = Table(
    'ReleaseAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('gripper', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_SearchAction = Table(
    'SearchAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('target_location_id', ForeignKey('PoseStamped.id'), nullable=False),
    Column('object_type', TypeType)
)

t_SetGripperAction = Table(
    'SetGripperAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('gripper', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('motion', Enum(pycram.datastructures.enums.GripperState), nullable=False)
)

t_TaskTreeNode = Table(
    'TaskTreeNode', metadata,
    Column('id', Integer, primary_key=True),
    Column('start_time', DateTime, nullable=False),
    Column('end_time', DateTime),
    Column('status', Enum(pycram.datastructures.enums.TaskStatus), nullable=False),
    Column('reason', String),
    Column('action_id', ForeignKey('ActionDescription.id')),
    Column('parent_id', ForeignKey('TaskTreeNode.id'))
)

t_TransportAction = Table(
    'TransportAction', metadata,
    Column('id', ForeignKey('ActionDescription.id'), primary_key=True),
    Column('arm', Enum(pycram.datastructures.enums.Arms), nullable=False),
    Column('target_location_id', ForeignKey('PoseStamped.id'), nullable=False),
    Column('object_at_execution_id', ForeignKey('FrozenObject.id'))
)

t_CodeNode = Table(
    'CodeNode', metadata,
    Column('id', ForeignKey('LanguageNode.id'), primary_key=True)
)

t_ParallelNode = Table(
    'ParallelNode', metadata,
    Column('id', ForeignKey('LanguageNode.id'), primary_key=True)
)

t_SequentialNode = Table(
    'SequentialNode', metadata,
    Column('id', ForeignKey('LanguageNode.id'), primary_key=True)
)

t_MonitorNode = Table(
    'MonitorNode', metadata,
    Column('id', ForeignKey('SequentialNode.id'), primary_key=True)
)

t_RepeatNode = Table(
    'RepeatNode', metadata,
    Column('id', ForeignKey('SequentialNode.id'), primary_key=True),
    Column('repeat', Integer, nullable=False)
)

t_TryAllNode = Table(
    'TryAllNode', metadata,
    Column('id', ForeignKey('ParallelNode.id'), primary_key=True)
)

t_TryInOrderNode = Table(
    'TryInOrderNode', metadata,
    Column('id', ForeignKey('SequentialNode.id'), primary_key=True)
)

mapper_registry = registry(metadata=metadata)

m_GraspDescription = mapper_registry.map_imperatively(pycram.datastructures.grasp.GraspDescription, t_GraspDescription, )

m_Vector3 = mapper_registry.map_imperatively(pycram.datastructures.pose.Vector3, t_Vector3, )

m_Quaternion = mapper_registry.map_imperatively(pycram.datastructures.pose.Quaternion, t_Quaternion, )

m_Pose = mapper_registry.map_imperatively(pycram.datastructures.pose.Pose, t_Pose, properties = dict(position=relationship('Vector3',foreign_keys=[t_Pose.c.position_id]), 
orientation=relationship('Quaternion',foreign_keys=[t_Pose.c.orientation_id])), polymorphic_on = "polymorphic_type", polymorphic_identity = "Pose")

m_Header = mapper_registry.map_imperatively(pycram.datastructures.pose.Header, t_Header, )

m_PoseStamped = mapper_registry.map_imperatively(pycram.datastructures.pose.PoseStamped, t_PoseStamped, properties = dict(pose=relationship('Pose',foreign_keys=[t_PoseStamped.c.pose_id]), 
header=relationship('Header',foreign_keys=[t_PoseStamped.c.header_id])), polymorphic_on = "polymorphic_type", polymorphic_identity = "PoseStamped")

m_ActionDescription = mapper_registry.map_imperatively(pycram.designator.ActionDescription, t_ActionDescription, properties = dict(robot_position=relationship('PoseStamped',foreign_keys=[t_ActionDescription.c.robot_position_id])), polymorphic_on = "polymorphic_type", polymorphic_identity = "ActionDescription")

m_PlanNode = mapper_registry.map_imperatively(pycram.plan.PlanNode, t_PlanNode, polymorphic_on = "polymorphic_type", polymorphic_identity = "PlanNode")

m_TaskTreeNode = mapper_registry.map_imperatively(pycram.orm.model.TaskTreeNode, t_TaskTreeNode, properties = dict(action=relationship('ActionDescription',foreign_keys=[t_TaskTreeNode.c.action_id]), 
parent=relationship('TaskTreeNode',foreign_keys=[t_TaskTreeNode.c.parent_id])))

m_FrozenObject = mapper_registry.map_imperatively(pycram.datastructures.dataclasses.FrozenObject, t_FrozenObject, properties = dict(pose=relationship('PoseStamped',foreign_keys=[t_FrozenObject.c.pose_id]), 
concept=t_FrozenObject.c.concept))

m_ORMActionNode = mapper_registry.map_imperatively(pycram.plan.ActionNode, t_ORMActionNode, )

m_ORMMotionNode = mapper_registry.map_imperatively(pycram.plan.MotionNode, t_ORMMotionNode, )

m_ORMResolvedActionNode = mapper_registry.map_imperatively(pycram.plan.ResolvedActionNode, t_ORMResolvedActionNode, properties = dict(designator_ref=relationship('ActionDescription',foreign_keys=[t_ORMResolvedActionNode.c.designator_ref_id])))

m_Transform = mapper_registry.map_imperatively(pycram.datastructures.pose.Transform, t_Transform, polymorphic_identity = "Transform", inherits = m_Pose)

m_TransformStamped = mapper_registry.map_imperatively(pycram.datastructures.pose.TransformStamped, t_TransformStamped, properties = dict(pose=relationship('Transform',foreign_keys=[t_TransformStamped.c.pose_id])), polymorphic_identity = "TransformStamped", inherits = m_PoseStamped)

m_GraspPose = mapper_registry.map_imperatively(pycram.datastructures.pose.GraspPose, t_GraspPose, properties = dict(grasp_description=relationship('GraspDescription',foreign_keys=[t_GraspPose.c.grasp_description_id])), polymorphic_identity = "GraspPose", inherits = m_PoseStamped)

m_MoveTorsoAction = mapper_registry.map_imperatively(pycram.designators.action_designator.MoveTorsoAction, t_MoveTorsoAction, polymorphic_identity = "MoveTorsoAction", inherits = m_ActionDescription)

m_SetGripperAction = mapper_registry.map_imperatively(pycram.designators.action_designator.SetGripperAction, t_SetGripperAction, polymorphic_identity = "SetGripperAction", inherits = m_ActionDescription)

m_ParkArmsAction = mapper_registry.map_imperatively(pycram.designators.action_designator.ParkArmsAction, t_ParkArmsAction, polymorphic_identity = "ParkArmsAction", inherits = m_ActionDescription)

m_NavigateAction = mapper_registry.map_imperatively(pycram.designators.action_designator.NavigateAction, t_NavigateAction, properties = dict(target_location=relationship('PoseStamped',foreign_keys=[t_NavigateAction.c.target_location_id])), polymorphic_identity = "NavigateAction", inherits = m_ActionDescription)

m_LookAtAction = mapper_registry.map_imperatively(pycram.designators.action_designator.LookAtAction, t_LookAtAction, properties = dict(target=relationship('PoseStamped',foreign_keys=[t_LookAtAction.c.target_id])), polymorphic_identity = "LookAtAction", inherits = m_ActionDescription)

m_OpenAction = mapper_registry.map_imperatively(pycram.designators.action_designator.OpenAction, t_OpenAction, polymorphic_identity = "OpenAction", inherits = m_ActionDescription)

m_CloseAction = mapper_registry.map_imperatively(pycram.designators.action_designator.CloseAction, t_CloseAction, polymorphic_identity = "CloseAction", inherits = m_ActionDescription)

m_FaceAtAction = mapper_registry.map_imperatively(pycram.designators.action_designator.FaceAtAction, t_FaceAtAction, properties = dict(pose=relationship('PoseStamped',foreign_keys=[t_FaceAtAction.c.pose_id])), polymorphic_identity = "FaceAtAction", inherits = m_ActionDescription)

m_SearchAction = mapper_registry.map_imperatively(pycram.designators.action_designator.SearchAction, t_SearchAction, properties = dict(target_location=relationship('PoseStamped',foreign_keys=[t_SearchAction.c.target_location_id]), 
object_type=t_SearchAction.c.object_type), polymorphic_identity = "SearchAction", inherits = m_ActionDescription)

m_DetectAction = mapper_registry.map_imperatively(pycram.designators.action_designator.DetectAction, t_DetectAction, properties = dict(object_at_execution=relationship('FrozenObject',foreign_keys=[t_DetectAction.c.object_at_execution_id])), polymorphic_identity = "DetectAction", inherits = m_ActionDescription)

m_GraspingAction = mapper_registry.map_imperatively(pycram.designators.action_designator.GraspingAction, t_GraspingAction, properties = dict(object_at_execution=relationship('FrozenObject',foreign_keys=[t_GraspingAction.c.object_at_execution_id])), polymorphic_identity = "GraspingAction", inherits = m_ActionDescription)

m_ReleaseAction = mapper_registry.map_imperatively(pycram.designators.action_designator.ReleaseAction, t_ReleaseAction, properties = dict(object_at_execution=relationship('FrozenObject',foreign_keys=[t_ReleaseAction.c.object_at_execution_id])), polymorphic_identity = "ReleaseAction", inherits = m_ActionDescription)

m_GripAction = mapper_registry.map_imperatively(pycram.designators.action_designator.GripAction, t_GripAction, properties = dict(object_at_execution=relationship('FrozenObject',foreign_keys=[t_GripAction.c.object_at_execution_id])), polymorphic_identity = "GripAction", inherits = m_ActionDescription)

m_ReachToPickUpAction = mapper_registry.map_imperatively(pycram.designators.action_designator.ReachToPickUpAction, t_ReachToPickUpAction, properties = dict(grasp_description=relationship('GraspDescription',foreign_keys=[t_ReachToPickUpAction.c.grasp_description_id]), 
object_at_execution=relationship('FrozenObject',foreign_keys=[t_ReachToPickUpAction.c.object_at_execution_id])), polymorphic_identity = "ReachToPickUpAction", inherits = m_ActionDescription)

m_PickUpAction = mapper_registry.map_imperatively(pycram.designators.action_designator.PickUpAction, t_PickUpAction, properties = dict(object_at_execution=relationship('FrozenObject',foreign_keys=[t_PickUpAction.c.object_at_execution_id])), polymorphic_identity = "PickUpAction", inherits = m_ActionDescription)

m_PlaceAction = mapper_registry.map_imperatively(pycram.designators.action_designator.PlaceAction, t_PlaceAction, properties = dict(target_location=relationship('PoseStamped',foreign_keys=[t_PlaceAction.c.target_location_id]), 
object_at_execution=relationship('FrozenObject',foreign_keys=[t_PlaceAction.c.object_at_execution_id])), polymorphic_identity = "PlaceAction", inherits = m_ActionDescription)

m_TransportAction = mapper_registry.map_imperatively(pycram.designators.action_designator.TransportAction, t_TransportAction, properties = dict(target_location=relationship('PoseStamped',foreign_keys=[t_TransportAction.c.target_location_id]), 
object_at_execution=relationship('FrozenObject',foreign_keys=[t_TransportAction.c.object_at_execution_id])), polymorphic_identity = "TransportAction", inherits = m_ActionDescription)

m_LanguageNode = mapper_registry.map_imperatively(pycram.language.LanguageNode, t_LanguageNode, properties = dict(action=relationship('ActionDescription',foreign_keys=[t_LanguageNode.c.action_id])), polymorphic_identity = "LanguageNode", inherits = m_PlanNode)

m_SequentialNode = mapper_registry.map_imperatively(pycram.language.SequentialNode, t_SequentialNode, polymorphic_identity = "SequentialNode", inherits = m_LanguageNode)

m_ParallelNode = mapper_registry.map_imperatively(pycram.language.ParallelNode, t_ParallelNode, polymorphic_identity = "ParallelNode", inherits = m_LanguageNode)

m_CodeNode = mapper_registry.map_imperatively(pycram.language.CodeNode, t_CodeNode, polymorphic_identity = "CodeNode", inherits = m_LanguageNode)

m_TryInOrderNode = mapper_registry.map_imperatively(pycram.language.TryInOrderNode, t_TryInOrderNode, polymorphic_identity = "TryInOrderNode", inherits = m_SequentialNode)

m_MonitorNode = mapper_registry.map_imperatively(pycram.language.MonitorNode, t_MonitorNode, polymorphic_identity = "MonitorNode", inherits = m_SequentialNode)

m_RepeatNode = mapper_registry.map_imperatively(pycram.language.RepeatNode, t_RepeatNode, polymorphic_identity = "RepeatNode", inherits = m_SequentialNode)

m_TryAllNode = mapper_registry.map_imperatively(pycram.language.TryAllNode, t_TryAllNode, polymorphic_identity = "TryAllNode", inherits = m_ParallelNode)
