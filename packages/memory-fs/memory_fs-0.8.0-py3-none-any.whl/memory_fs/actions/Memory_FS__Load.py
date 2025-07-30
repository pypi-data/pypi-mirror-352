from typing                                             import Optional, Any
from memory_fs.actions.Memory_FS__Data                  import Memory_FS__Data
from memory_fs.actions.Memory_FS__Deserialize           import Memory_FS__Deserialize
from memory_fs.actions.Memory_FS__Paths                 import Memory_FS__Paths
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File          import Schema__Memory_FS__File
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Memory_FS__Load(Type_Safe):
    storage     : Memory_FS__Storage

    @cache_on_self
    def memory_fs__data(self):
        return Memory_FS__Data(storage=self.storage)


    @cache_on_self
    def memory_fs__deserialize(self):
        return Memory_FS__Deserialize(storage=self.storage)

    def memory_fs__paths(self, file_config : Schema__Memory_FS__File__Config):
        return Memory_FS__Paths(file__config=file_config)


    def load(self, file_config : Schema__Memory_FS__File__Config  # Load file from the appropriate path based on config
              ) -> Optional[Schema__Memory_FS__File]:
        full_file_paths = self.memory_fs__paths(file_config=file_config).paths()
        for full_file_path in full_file_paths:
            file = self.memory_fs__data().load(full_file_path)
            if file:
                return file
        return None

    def load_content(self, file_config : Schema__Memory_FS__File__Config  # Load content for a file
                      ) -> Optional[bytes]:
        full_file_paths = self.memory_fs__paths(file_config=file_config).paths__content()
        for full_file_path in full_file_paths:
            content_bytes  = self.memory_fs__data().load_content(full_file_path)
            if content_bytes:
                return content_bytes
        return None

    def load_data(self, file_config : Schema__Memory_FS__File__Config  # Load and deserialize file data
                  ) -> Optional[Any]:
        # Load raw content
        content_bytes = self.load_content(file_config)
        if not content_bytes:
            return None

        # Deserialize based on file type
        return self.memory_fs__deserialize()._deserialize_data(content_bytes, file_config.file_type)
