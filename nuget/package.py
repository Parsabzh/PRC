class Package:
    def __init__(self, url,package_id, version, name= None,author = None, license = None , description= None):
        self.url = url
        self.package_id = package_id
        self.version = version
        self.name = name
        self.author = author
        self.license = license
        self.description = description
        
    def to_dict(self):
        package_dict = {
            'url': self.url,
            'package_id': self.package_id,
            'version': self.version,
            'name': self.name,
            'author': self.author,
            'license': self.license,
            'description': self.description
        }
        return package_dict
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
