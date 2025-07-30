from typing                                                 import Any, Dict
from memory_fs.actions.Memory_FS__Edit                      import Memory_FS__Edit
from memory_fs.actions.Memory_FS__Serialize                 import Memory_FS__Serialize
from memory_fs.schemas.Schema__Memory_FS__File              import Schema__Memory_FS__File
from memory_fs.schemas.Schema__Memory_FS__File__Metadata    import Schema__Memory_FS__File__Metadata
from memory_fs.schemas.Schema__Memory_FS__File__Type        import Schema__Memory_FS__File__Type
from memory_fs.storage.Memory_FS__Storage                   import Memory_FS__Storage
from osbot_utils.helpers.safe_str.Safe_Str__Hash            import safe_str_hash
from memory_fs.schemas.Enum__Memory_FS__File__Encoding      import Enum__Memory_FS__File__Encoding
from osbot_utils.decorators.methods.cache_on_self           import cache_on_self
from osbot_utils.helpers.Safe_Id                            import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path      import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config      import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                        import Type_Safe


class Memory_FS__Save(Type_Safe):
    storage     : Memory_FS__Storage

    @cache_on_self
    def memory_fs__edit(self):
        return Memory_FS__Edit(storage=self.storage)

    @cache_on_self
    def memory_fs__serialize(self):
        return Memory_FS__Serialize(storage=self.storage)

    def save(self, file_data   : Any,  # Save file data using all configured path handlers
                   file_config : Schema__Memory_FS__File__Config
              ) -> Dict[Safe_Id, Safe_Str__File__Path]:

        # Get file type from config
        file_type = file_config.file_type
        if type(file_type) is Schema__Memory_FS__File__Type:            # means that is it the default class (which should be abstracted)
            raise ValueError("file_config.file_type is required")     # todo: see if we still need this (also this check should happen inside the _serialize_data method, since that is the one that needs this data)

        # Convert data to bytes based on file type's serialization method
        content_bytes = self.memory_fs__serialize()._serialize_data(file_data, file_type)

        # Calculate content hash and size
        if file_type.encoding == Enum__Memory_FS__File__Encoding.BINARY:
            content_hash = safe_str_hash(str(content_bytes))
        else:
            content_hash = safe_str_hash(content_bytes.decode(file_type.encoding.value))

        content_size = len(content_bytes)
        saved_paths  = []
        metadata     = Schema__Memory_FS__File__Metadata(content__hash  = content_hash ,
                                                         content__size  = content_size )

        file = Schema__Memory_FS__File(config  = file_config,                           # Create the complete file
                                      metadata = metadata )

        saved_pages__file    = self.memory_fs__edit().save        (file_config = file_config, file    = file         )
        saved_pages__content = self.memory_fs__edit().save_content(file_config = file_config, content = content_bytes)

        saved_paths.extend(saved_pages__file   )
        saved_paths.extend(saved_pages__content)

        return sorted(saved_paths)