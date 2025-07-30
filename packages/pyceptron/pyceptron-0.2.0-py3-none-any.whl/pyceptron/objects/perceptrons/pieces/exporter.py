from ..models.perceptronABC import PerceptronABC
import json
from os.path import exists, join

class ExportPerceptronPiece(PerceptronABC):
  def _dumps_format(self, path):
    data = {
      "name": self.name,
      "f_activation": self.f_activation.name,
      "weights": [
        float(w) for w in self.weights
      ],
      "bias": float(self.bias),
    }
    json.dump(data, open(path, "w"))
    self._analyzer_middleware.console.success(f"Perceptron saved in {path}")

  def save(self, name:str=None, dir:str=".", overwrite:bool=False) -> None:
    if not exists(dir):
      raise FileNotFoundError(f"No such directory '{dir}'")

    ext_file = ".json"

    if name:
      if not name.endswith(ext_file):
        name = name+ext_file
      pathfile = join(dir, name)
      if not overwrite and exists(pathfile):
        raise FileExistsError("File name exists in {}".format(dir))
      else:
        self._dumps_format(pathfile)
        return

    name = "perceptron"
    pathfile = join(dir, name+ext_file)

    if exists(pathfile) and not overwrite:
      c = 1
      pathfile = join(dir, name+str(c)+ext_file)
      while exists(pathfile):
        c += 1
        pathfile = join(dir, name+str(c)+ext_file)
      else:
        self._dumps_format(pathfile)

    else:
      self._dumps_format(pathfile)
