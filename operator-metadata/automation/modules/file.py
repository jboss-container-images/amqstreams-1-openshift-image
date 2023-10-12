class File:
  def __init__(self, path):
    with open(path, 'r') as file:
      self.data = file.read().rstrip()
    self.path = path

  def get_data(self):
    return self.data

  def get_path(self):
    return self.path

  def write(self):
    with open(self.path, 'w') as sources:
      sources.write(self.data)

  def write(self, path):
    with open(path, 'w') as sources:
      sources.write(self.data)