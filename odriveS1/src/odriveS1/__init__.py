"""
This files odriveS1 model with the Viam Registry.
"""

from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.components.motor import Motor
from .odriveS1 import OdriveS1
from .odriveCAN import OdriveCAN

Registry.register_resource_creator(Motor.SUBTYPE, OdriveS1.MODEL, ResourceCreatorRegistration(OdriveS1.new))
Registry.register_resource_creator(Motor.SUBTYPE, OdriveCAN.MODEL, ResourceCreatorRegistration(OdriveCAN.new))