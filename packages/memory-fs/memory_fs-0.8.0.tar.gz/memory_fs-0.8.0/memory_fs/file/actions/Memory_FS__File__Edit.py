from typing                                             import Any
from memory_fs.actions.Memory_FS__Data                  import Memory_FS__Data
from memory_fs.actions.Memory_FS__Paths                 import Memory_FS__Paths
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.actions.Memory_FS__Edit                  import Memory_FS__Edit
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Memory_FS__File__Edit(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage      : Memory_FS__Storage

    @cache_on_self
    def storage_data(self):
        return Memory_FS__Data(storage=self.storage)

    @cache_on_self
    def storage_edit(self):
        return Memory_FS__Edit(storage=self.storage)

    def storage_paths(self):
        return Memory_FS__Paths(file__config=self.file__config)

    def load__content(self):
        paths = self.storage_paths().paths__content()
        if paths:
            path  = paths[0]                    # todo: this logic should be inside the storage_data
            return self.storage_data().load_content(path)

    def save__content(self, content: Any):
        return self.storage_edit().save_content(self.file__config, content)

