from memory_fs.actions.Memory_FS__Delete            import Memory_FS__Delete
from memory_fs.actions.Memory_FS__Load              import Memory_FS__Load
from memory_fs.actions.Memory_FS__Save              import Memory_FS__Save
from memory_fs.storage.Memory_FS__Storage           import Memory_FS__Storage
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from memory_fs.actions.Memory_FS__Data              import Memory_FS__Data
from memory_fs.actions.Memory_FS__Edit              import Memory_FS__Edit
from osbot_utils.type_safe.Type_Safe                import Type_Safe


class Memory_FS(Type_Safe):
    storage     : Memory_FS__Storage

    @cache_on_self
    def data(self):
        return Memory_FS__Data(storage=self.storage)

    @cache_on_self
    def delete(self):
        return Memory_FS__Delete(storage=self.storage)

    @cache_on_self
    def edit(self):
        return Memory_FS__Edit(storage=self.storage)

    @cache_on_self
    def load(self):
        return Memory_FS__Load(storage=self.storage)

    @cache_on_self
    def save(self):
        return Memory_FS__Save(storage=self.storage)
