"""Home Assistant module for Shiny API."""
import inspect
import logging
from typing import Callable
from homeassistant_api import Client, Domain, Entity
from shiny_app.classes.config import Config


class HomeAssistant:
    """Base Class for HomeAsssitant module"""

    domain: str

    def __init__(self, entity_id: str, location: str = "store1"):
        """Get Home Assistant client"""

        if self.domain == "":
            logging.error("Domain not set")
            return
        self.client = Client(
            Config.HOMEASSISTANT_API[location]["url"],
            Config.HOMEASSISTANT_API[location]["key"],
        )
        self.entity_id: str = f"{self.domain}.{entity_id}"

    @classmethod
    def get_functions(cls) -> list[str]:
        """Return functions"""
        methods = [method for method, _ in inspect.getmembers(cls, predicate=inspect.isfunction) if not method.startswith("__")]
        return methods

    def status(self):
        """Get input boolean status"""
        entity = self.client.get_entity(entity_id=self.entity_id)
        if not isinstance(entity, Entity):
            return "entity not found"
        return entity.get_state().state


class Vacuum(HomeAssistant):
    """Class for Roomba vacuum cleaner"""

    def __init__(self, entity_id: str = "roomba_pt", **kwargs):
        self.domain = "vacuum"
        super().__init__(entity_id=entity_id, **kwargs)

    def suck(self) -> str:
        """Start vacuum cleaner"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.start(entity_id=self.entity_id)
        return "starting"

    def stop(self) -> str:
        """Return vacuum cleaner to base"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.stop(entity_id=self.entity_id)
        return "stopping"

    def go_home(self) -> str:
        """Return vacuum cleaner to base"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.return_to_base(entity_id=self.entity_id)
        return "going home"


class InputBoolean(HomeAssistant):
    """Testing class"""

    def __init__(self, *args, **kwargs):
        self.domain = "input_boolean"
        super().__init__(*args, **kwargs)

    def turn_on(self) -> str:
        """Turn on input boolean"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.turn_on(entity_id=self.entity_id)
        return "Turning on"

    def turn_off(self) -> str:
        """Turn off input boolean"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.turn_off(entity_id=self.entity_id)
        return "Turning off"

    def toggle(self) -> str:
        """Toggle input boolean"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.toggle(entity_id=self.entity_id)
        return "Toggling"


class Alarm(HomeAssistant):
    """Class for Alarm panel"""

    def __init__(self, entity_id: str = "system", **kwargs):
        self.domain = "alarm_control_panel"
        super().__init__(entity_id=entity_id, **kwargs)

    def arm(self) -> str:
        """Arm alarm panel"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.alarm_arm_away(entity_id=self.entity_id)
        return "arming"

    def disarm(self) -> str:
        """Arm alarm panel"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.alarm_disarm(entity_id=self.entity_id)
        return "disarming"


class Lock(HomeAssistant):
    """Class for Locks"""

    def __init__(self, *args, **kwargs):
        self.domain = "lock"
        super().__init__(*args, **kwargs)

    def lock(self) -> str:
        """Lock door"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.lock(entity_id=self.entity_id)
        return "locking"

    def unlock(self) -> str:
        """Unlock door"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.unlock(entity_id=self.entity_id)
        return "unlocking"


class Sensor(HomeAssistant):
    """Sensor class"""

    def __init__(self, *args, **kwargs):
        self.domain = "sensor"
        super().__init__(*args, **kwargs)


class Button(HomeAssistant):
    """Button class"""

    def __init__(self, *args, **kwargs):
        self.domain = "button"
        super().__init__(*args, **kwargs)

    def press(self) -> str:
        """Start button"""
        ha_domain = self.client.get_domain(self.domain)
        if not isinstance(ha_domain, Domain):
            return "domain not found"
        ha_domain.press(entity_id=self.entity_id)  # pyright: reportOptionalCall=false
        return "starting"


class TaylorSwiftly:
    """Class for Taylor Swiftly"""

    def __init__(self):
        self.battery = Sensor("taylor_swiftly_battery", location="home")
        self.lock = Lock("taylor_swiftly_doors", location="home")
        self.start = Button("taylor_swiftly_remote_start", location="home")

    def get_functions(self) -> dict[str, Callable]:
        """Return functions"""
        methods = {}
        for class_name, class_method in vars(self).items():
            for name in class_method.get_functions():
                methods[f"{name} {class_name}"] = getattr(class_method, name)
        return methods


if __name__ == "__main__":
    taylor = TaylorSwiftly()
    print(taylor.battery.status())
