from memory_fs.file.actions.Memory_FS__File__Data       import Memory_FS__File__Data
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Memory_FS__File__Create(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage      : Memory_FS__Storage

    @cache_on_self
    def file_data(self):
        return Memory_FS__File__Data(file__config=self.file__config, storage=self.storage)

    def create(self):
        with self.file_data() as _:
            if _.exists() is False:
                return _.paths()                # todo: finish implementation of this method
                return 'creating'

    def exists(self):
        return self.file_data().exists()