from unittest import mock

import pytest
from ophyd import Component as Cpt
from ophyd import Device, Signal

from bec_lib.bec_errors import DeviceConfigError
from bec_server.device_server.devices.device_serializer import get_device_info


class MyDevice(Device):
    custom = Cpt(Signal, value=0)


class DummyDeviceWithConflictingSignalNames(Device):
    # This device has a signal with the same name as a protected method
    # in the Device class
    enabled = Cpt(Signal, value=0)


class DummyDeviceWithConflictingName(Device):
    """This device will be assigned a protected name"""


class DummyDeviceWithConflictingUserAccess(Device):
    """This device will be assigned a protected name"""

    USER_ACCESS = ["enabled"]

    def enabled(self):
        pass


class DummyDeviceWithConflictingSubDevice(Device):
    """This device will be assigned a protected name"""

    sub_device = Cpt(DummyDeviceWithConflictingSignalNames)


@pytest.mark.parametrize(
    "obj",
    [
        DummyDeviceWithConflictingSignalNames(name="test"),
        DummyDeviceWithConflictingSignalNames(name="enabled"),
        DummyDeviceWithConflictingSubDevice(name="test"),
        DummyDeviceWithConflictingUserAccess(name="test"),
    ],
)
def test_get_device_info(obj):
    with pytest.raises(DeviceConfigError):
        _ = get_device_info(obj)


def test_get_device_info_without_connection():
    device = MyDevice(name="test")
    with (
        mock.patch.object(device, "describe", side_effect=TimeoutError),
        mock.patch.object(device, "describe_configuration", side_effect=TimeoutError),
        mock.patch.object(device.custom, "describe", side_effect=TimeoutError),
        mock.patch.object(device.custom, "describe_configuration", side_effect=TimeoutError),
        mock.patch.object(device, "walk_components", side_effect=TimeoutError),
    ):
        _ = get_device_info(device, connect=False)
