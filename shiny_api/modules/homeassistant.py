"""Home Assistant module for Shiny API."""
import inspect
import os
from homeassistant_api import Client
import shiny_api.modules.load_config as config

print(f"Importing {os.path.basename(__file__)}...")


class HomeAssistant:
    """Base Class for HomeAsssitant module"""

    def __init__(self, entity_id: str, location: str = "store1"):
        """Get Home Assistant client"""
        self.domain = self.domain or ""
        self.client = Client(
            config.HOMEASSISTANT_API[location]["url"],
            config.HOMEASSISTANT_API[location]["key"],
        )
        self.entity_id = f"{self.domain}.{entity_id}"

    @classmethod
    def get_functions(cls):
        """Return functions"""
        methods = [method for method, _ in inspect.getmembers(cls, predicate=inspect.isfunction) if not method.startswith("__")]
        return methods

    def status(self):
        """Get input boolean status"""
        return self.client.get_entity(entity_id=self.entity_id).get_state().state


class Vacuum(HomeAssistant):
    """Class for Roomba vacuum cleaner"""

    def __init__(self, *args, entity_id: str = "roomba_pt", **kwargs):
        self.domain = "vacuum"
        super().__init__(entity_id=entity_id, *args, **kwargs)

    def start(self):
        """Start vacuum cleaner"""
        self.client.get_domain(self.domain).start(entity_id=self.entity_id)

    def stop(self):
        """Return vacuum cleaner to base"""
        print(f"{self.entity_id}|{self.domain}")
        self.client.get_domain(self.domain).stop(entity_id=self.entity_id)

    def go_home(self):
        """Return vacuum cleaner to base"""
        self.client.get_domain(self.domain).return_to_base(entity_id=self.entity_id)


class InputBoolean(HomeAssistant):
    """Testing class"""

    def __init__(self, *args, **kwargs):
        self.domain = "input_boolean"
        super().__init__(*args, **kwargs)

    def turn_on(self):
        """Turn on input boolean"""
        self.client.get_domain(self.domain).turn_on(entity_id=self.entity_id)

    def turn_off(self):
        """Turn off input boolean"""
        self.client.get_domain(self.domain).turn_off(entity_id=self.entity_id)

    def toggle(self):
        """Toggle input boolean"""
        self.client.get_domain(self.domain).toggle(entity_id=self.entity_id)


class Alarm(HomeAssistant):
    """Class for Alarm panel"""

    def __init__(self, *args, entity_id: str = "system", **kwargs):
        self.domain = "alarm_control_panel"
        super().__init__(entity_id=entity_id * args, **kwargs)

    def arm(self):
        """Arm alarm panel"""
        self.client.get_domain(self.domain).alarm_arm_away(entity_id=self.entity_id)

    def disarm(self):
        """Arm alarm panel"""
        self.client.get_domain(self.domain).alarm_disarm(entity_id=self.entity_id)


class Lock(HomeAssistant):
    """Class for Locks"""

    def __init__(self, *args, **kwargs):
        self.domain = "lock"
        super().__init__(*args, **kwargs)

    def lock(self):
        """Lock door"""
        self.client.get_domain(self.domain).lock(entity_id=self.entity_id)

    def unlock(self):
        """Unlock door"""
        self.client.get_domain(self.domain).unlock(entity_id=self.entity_id)


class Sensor(HomeAssistant):
    def __init__(self, *args, **kwargs):
        self.domain = "sensor"
        super().__init__(*args, **kwargs)


class TaylorSwiftly:
    """Class for Taylor Swiftly Lock"""

    def __init__(self):
        self.battery = Sensor("taylor_swiftly_battery", location="home")
        self.lock = Lock("taylor_swiftly_doors", location="home")

    def get_functions(self):
        """Return functions"""
        methods = {}
        for class_name, class_method in vars(self).items():
            for name in class_method.get_functions():
                methods[f"{name} {class_name}"] = getattr(class_method, name)
        return methods


if __name__ == "__main__":
    # test = InputBoolean("testing")
    # print(test.status)
    taylor_lock = Lock("taylor_swiftly_doors", location="home")
    taylor_batt = Sensor("taylor_swiftly_battery", location="home")
    # taylor.lock()
    taylor = TaylorSwiftly()
    # taylor.get_functions()["lock lock"]()
    print(taylor.get_functions())
    print(taylor.battery.s)
