from typing                                             import List, Type
from memory_fs.path_handlers.Path__Handler__Latest      import Path__Handler
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Schema__Memory_FS__File__Storage__Config(Type_Safe):
    path_handlers : List[Type[Path__Handler]]

class Memory_FS__File__Storage(Type_Safe):
    config: Schema__Memory_FS__File__Storage__Config

    def file__paths(self):
        file_paths = []
        for path_handler in self.config.path_handlers:
            file_path  = path_handler().generate_path()
            file_paths.append(file_path)
        return file_paths