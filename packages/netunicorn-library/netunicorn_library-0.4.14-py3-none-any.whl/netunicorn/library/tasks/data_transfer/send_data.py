import requests
from netunicorn.base import Failure, Success, Task
from dataclasses import dataclass
from typing import Callable, Any, Literal, Optional

class SendData(Task):
    """
    Sends a netunicorn speedtest execution result(s) to an API endpoint
    """
    
    @dataclass
    class TaskDescriptor:
        name: str
        datatype: Literal["ookla-speedtest", "mlab-speedtest"]
        handler: Optional[Callable[[Any], Any]]

    def __init__(
        self, 
        task_descriptors: list[TaskDescriptor], 
        endpoint: str, 
        allow_failure = False,
	payload_handler: Optional[Callable[[Any], Any]] = None,
        *args, 
        **kwargs
        ):
        
        self.task_descriptors = task_descriptors
        self.endpoint = endpoint
        self.allow_failure = allow_failure
        self.payload_handler = payload_handler
        super().__init__(*args, **kwargs)

    def get_geolocation_from_ip(self, ip: str): 
        """
        Get the geolocation of an IP address using ip-api.com.
        """
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}")
            location_data = response.json()

            if location_data and 'city' in location_data:
                city = location_data['city']
                loc = location_data.get('loc', '34.0549,118.2426')
                lat, lon = loc.split(',')
                return (city, float(lat), float(lon))
            else:
                return ("losangeles", 34.0549, 118.2426)
        
        except Exception as e:
            print(f"Error fetching geolocation: {e}")
            return ("losangeles", 34.0549, 118.2426)
    
    def run(self):
        import uuid
        
        try:
            execution_results = []
            for task_descriptor in self.task_descriptors:            
                raw_task_result = self.previous_steps.get(task_descriptor.name, Failure(f"{task_descriptor.name} not found"))

                if isinstance(raw_task_result, Failure) and not self.allow_failure:
                    return raw_task_result
                if isinstance(raw_task_result, Failure):
                    continue

                raw_results = [result.unwrap() for result in raw_task_result]
                
                if task_descriptor.handler:
                    task_results = task_descriptor.handler(task_descriptor.datatype, raw_results)
                else: # no handler
                    task_results = {
                    "task_type": task_descriptor.datatype,
                    "task_results": raw_results
                    }
                execution_results.append(task_results)
            
            (location_str, *_) = self.get_geolocation_from_ip("8.8.8.8")

            measurement_data = {"execution_results": execution_results}

            payload = {
                    "client_location": location_str,
            "measurement_type": self.task_descriptors[0].datatype,
            "measurement_data": measurement_data
                }

            if self.payload_handler:
                    payload = self.payload_handler(payload)
 
            response = requests.post(self.endpoint, json=payload)

            if response.status_code == 200:
                return Success(response.json())
            else:
                return Failure(f"Failed to transfer data:\n {response.status_code} {response.text}")
            
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")
