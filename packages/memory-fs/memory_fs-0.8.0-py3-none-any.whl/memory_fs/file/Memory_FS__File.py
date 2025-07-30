from memory_fs.file.actions.Memory_FS__File__Create     import Memory_FS__File__Create
from memory_fs.file.actions.Memory_FS__File__Data       import Memory_FS__File__Data
from memory_fs.file.actions.Memory_FS__File__Edit       import Memory_FS__File__Edit
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Memory_FS__File(Type_Safe):
    file_config : Schema__Memory_FS__File__Config
    storage     : Memory_FS__Storage

    @cache_on_self
    def create(self):
        return Memory_FS__File__Create(file__config=self.file_config, storage=self.storage)

    @cache_on_self
    def data(self):
        return Memory_FS__File__Data(file__config=self.file_config, storage= self.storage)

    @cache_on_self
    def edit(self):
        return Memory_FS__File__Edit(file__config=self.file_config, storage= self.storage)


    # helper methods that are very common in files          # todo: see if we need them (i.e. are they really useful and make it easy for dev's experience)

    def exists(self):
        return self.data().exists()