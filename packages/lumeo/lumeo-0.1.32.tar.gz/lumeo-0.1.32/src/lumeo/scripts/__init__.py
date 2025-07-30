import pkgutil

def list():
    """
    Lists all the executable scripts within all subpackages and modules of this package.

    Returns:
        list: A list of strings representing the paths to the executable scripts.
    """
    scripts = []
    package = __import__('lumeo.scripts', fromlist=[''])
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if not ispkg:
            try:
                module = __import__(modname, fromlist=[''])
                if hasattr(module, 'main'):
                    scripts.append(modname)
            except Exception as e:
                pass

    sanitized_scripts = []    
    for script in scripts:
        sanitized_script = script.replace('.scripts.', '.').replace('.__main__', '').replace('_', '-').replace('.','-')  
        sanitized_scripts.append(sanitized_script)
        print(sanitized_script)
                      
    return 0

if __name__ == "__main__":
    list()