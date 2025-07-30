def log_event(severity="info", event_type=None, payload=None, print_to_console=True):
    """
    Log a Lumeo event with a specified severity, event type, and payload.
    More about Lumeo events: https://docs.lumeo.com/docs/event
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).

    Args:
        severity (str): The severity level of the event. Must be one of ["debug", "info", "warning", "error"].
        event_type (str): The type of the event.
        payload (str): The payload of the event.
        print_to_console (bool): Whether to print the event to the console. Default is True.

    Raises:
        ValueError: If the severity is not in the available severities.
        ValueError: If the event_type is empty or missing.
        ValueError: If the payload is empty or missing.
    """
    # `event_sender` module is defined in `lumeopython` GStreamer element, so it's not available
    # during Python unit tests.
    import event_sender

    available_severities = ["debug", "info", "warning", "error"]

    if severity not in available_severities:
        raise ValueError("'severity' value is not in {}".format(available_severities))

    if not event_type:
        raise ValueError("'event_type' is empty or missing")

    if not payload:
        raise ValueError("'payload' is empty or missing")

    event_sender.send(severity, event_type, payload)

    if print_to_console:
        print(f"Event: {severity} - {event_type} - {payload}")


def error_log(object_to_log, node_id=""):
    """
    Log an error event.
    More about Lumeo events: https://docs.lumeo.com/docs/event
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).

    Args:
        object_to_log (str): The object to log.
        node_id (str): The ID of the node. Default is an empty string.
    """
    print("{} Error : {}".format(node_id, object_to_log))
    log_event("error", "deployment.error.node", f"{node_id} Error : {object_to_log}")


def warning_log(object_to_log, node_id=""):
    """
    Log a warning event.
    More about Lumeo events: https://docs.lumeo.com/docs/event
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).
    
    Args:
        object_to_log (str): The object to log.
        node_id (str): The ID of the node. Default is an empty string.
    """
    print("{} Warning : {}".format(node_id, object_to_log))
    log_event("warning", "deployment.warning.node", f"{node_id} Warning : {object_to_log}")


def info_log(object_to_log, node_id=""):
    """
    Log an info event.
    More about Lumeo events: https://docs.lumeo.com/docs/event
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).
    
    Args:
        object_to_log (str): The object to log.
        node_id (str): The ID of the node. Default is an empty string.
    """
    print("{} Info : {}".format(node_id, object_to_log))
    log_event("info", "deployment.info.node", f"{node_id} : {object_to_log}")


def debug_log(object_to_log, node_id=""):
    """
    Log a debug message to deployment console logs (Console -> Deployment detail -> Logs).
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).
    
    Args:
        object_to_log (str): The object to log.
        node_id (str): The ID of the node. Default is an empty string.
    """
    print("{} : {}".format(node_id, object_to_log))
    log_event("debug", "deployment.debug.node", f"{node_id} : {object_to_log}")


def debug_log_if(object_to_log, condition, node_id=""):
    """
    Log a debug message to deployment console logs if a condition is met.
    (Console -> Deployment detail -> Logs)
    
    Args:
        object_to_log (str): The object to log.
        condition (bool): The condition to check.
        node_id (str): The ID of the node. Default is an empty string.
    """
    if condition:
        print("{} : {}".format(node_id, object_to_log))


