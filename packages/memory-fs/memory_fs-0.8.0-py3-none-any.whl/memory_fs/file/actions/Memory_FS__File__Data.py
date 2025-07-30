from memory_fs.actions.Memory_FS__Data                  import Memory_FS__Data
from memory_fs.actions.Memory_FS__Paths                 import Memory_FS__Paths
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Memory_FS__File__Data(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage      : Memory_FS__Storage

    @cache_on_self
    def memory_fs__data(self):
        return Memory_FS__Data(storage=self.storage)

    def memory_fs__paths(self):
        return Memory_FS__Paths(file__config=self.file__config)

    def exists(self):
        return self.memory_fs__data().exists(file_config=self.file__config)

    def paths(self):
        return self.memory_fs__paths().paths()

