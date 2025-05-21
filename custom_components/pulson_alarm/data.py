"""Custom types for pulson_alarm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import IntegrationPulsonAlarmApiClient
    from .coordinator import PulsonAlarmDataUpdateCoordinator


type IntegrationPulsonAlarmConfigEntry = ConfigEntry[IntegrationPulsonAlarmData]


@dataclass
class IntegrationPulsonAlarmData:
    """Data for the PulsonAlarm integration."""

    client: IntegrationPulsonAlarmApiClient
    coordinator: PulsonAlarmDataUpdateCoordinator
    integration: Integration
