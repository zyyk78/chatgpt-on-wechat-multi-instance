def singleton(cls):
    instances = {}  # {instance_name: instance}

    def get_instance(*args, **kwargs):
        # Extract instance_name from kwargs but keep it in kwargs for the constructor
        instance_name = kwargs.get('_instance_name', "")
        if instance_name not in instances:
            instances[instance_name] = cls(*args, **kwargs)
        return instances[instance_name]

    get_instance._clear = lambda name: instances.pop(name, None)
    get_instance._clear_all = lambda: instances.clear()
    get_instance._instances = instances
    return get_instance
