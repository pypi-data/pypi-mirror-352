import pika
import json
import logging
from datetime import datetime, timezone
import threading
import time
from typing import Dict, Any, List, Optional, Union
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.utils.common import ServiceAbstract, get_mission_upload_dir
from vyomcloudbridge.constants.constants import (
    DEFAULT_RABBITMQ_URL,
    default_project_id,
    default_mission_id,
    data_buffer_key,
)
from vyomcloudbridge.utils.configs import Configs


class MachineStats(ServiceAbstract):
    """
    A service that maintains machine buffer statistics using RabbitMQ as a persistent store.
    Stores the current buffer state in a dedicated queue and publishes stats to HQ.
    """

    def __init__(self):
        """
        Initialize the machine stats service with RabbitMQ connection.
        """
        super().__init__()
        self.host: str = "localhost"
        self.rabbitmq_url = DEFAULT_RABBITMQ_URL
        self.priority = 2  # live priority
        self.stats_publish_interval = 1  # Seconds between stats publication
        self.publish_error_delay = 20  # Delay after publish error

        self.connection = None
        self.channel = None
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.data_source = "machine_stats"

        # Thread attributes
        self.stats_thread = None
        self.is_running = False

    def on_mission_data_publish(
            self,
            mission_data: Union[Dict, List[Dict]],  # mission_data can be a single dict or a list of dicts  
        ):
            """
            Update mission data statistics for a specific mission or multiple missions.
            Args:
                mission_data: A single mission data dictionary or a list of dictionaries.
                Each dictionary should contain:
                    - mission_id: int or str (default: "_all_")
                    - size: int
                    - data_type: str
                    - data_source: str
            """
            
            if not isinstance(mission_data, list):
                mission_data = [mission_data]
            
            if len(mission_data) == 0:
                self.logger.warning("No mission data provided to on_mission_data_publish")
                return
            
            if not self._ensure_connection():
                self.logger.error("Could not establish connection to RabbitMQ")
                raise Exception("Could not establish connection")
            
            total_data_published = 0
            for data in mission_data:
                mission_id = data.get("mission_id", None)
                if mission_id is not None and mission_id != data_buffer_key:
                    try:
                        mission_id = int(mission_id)
                    except ValueError:
                        self.logger.warning(
                            f"Invalid mission_id {mission_id}, using '_all_' instead"
                        )
                        mission_id = "_all_"
                    
                else:
                    mission_id = "_all_"

                size = data.get("size", 0)
                data_type = data.get("data_type", "unknown")
                data_source = data.get("data_source", self.data_source)

                if not mission_id:
                    self.logger.warning("Cannot add mission data: mission_id is empty")
                    continue
                if not size:
                    self.logger.warning("Mission data size is zero, skipping...")
                    continue

                
                new_mission_stats = "self.get_stats_from_rabbitmq(mission_id)"

                # Find matching entry or create new one
                found = False
                updated_at = datetime.now(timezone.utc).isoformat()
                for entry in new_mission_stats:
                    if entry["data_type"] == data_type and entry["data_source"] == data_source:
                        entry["file_count_uploaded"] += 1
                        entry["data_size_uploaded"] += size
                        entry["updated_at"] = updated_at
                        found = True
                        break

                # If no matching entry, create a new one
                if not found:
                    self.logger.warning(
                        f"mission data for mission_id was not tracked: {mission_id}, data_type: {data_type}, data_source: {data_source}"
                    )

                # If not found, new_mission created
                last_data_mission_id = self._get_last_data_mission_id()
                if last_data_mission_id and last_data_mission_id != mission_id:
                    self._publish_stats_to_hq(last_data_mission_id)
                self._set_last_data_mission(mission_id)
                self._update_stats_in_rabbitmq(mission_id, new_mission_stats)

                self.logger.info(
                    f"mission data updated for mission_id: {mission_id}, data_type: {data_type}, data_source: {data_source}"
                )
            
            self.machine_stats.on_data_publish(size)