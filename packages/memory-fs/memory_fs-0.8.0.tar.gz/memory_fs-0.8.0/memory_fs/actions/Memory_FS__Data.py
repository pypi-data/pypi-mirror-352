from typing                                                 import List, Optional, Dict, Any
from osbot_utils.type_safe.decorators.type_safe             import type_safe
from memory_fs.actions.Memory_FS__Paths                     import Memory_FS__Paths
from memory_fs.schemas.Schema__Memory_FS__File__Config      import Schema__Memory_FS__File__Config
from memory_fs.schemas.Schema__Memory_FS__File              import Schema__Memory_FS__File
from memory_fs.storage.Memory_FS__Storage                   import Memory_FS__Storage
from osbot_utils.helpers.Safe_Id                            import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path      import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                        import Type_Safe

class Memory_FS__Data(Type_Safe):
    storage     : Memory_FS__Storage

    def paths(self, file_config : Schema__Memory_FS__File__Config):
        return Memory_FS__Paths(file__config=file_config)

    @type_safe
    def exists(self, file_config : Schema__Memory_FS__File__Config
                ) -> bool:                                                          # todo: see if we need to add the default path (or to have a separate "exists strategy")
        files = self.storage.files()
        for full_file_path in self.paths(file_config).paths():
            if full_file_path in files:                                             # todo: refactor since this is going to be platform specific (specially since we shouldn't circle through all files to see if the file exists)
                return True                                                         # we only check if we found one of them
        return False                                                                # if none were found, return False

    @type_safe
    def exists_content(self, file_config : Schema__Memory_FS__File__Config
                 ) -> bool:
        content_files =  self.storage.content_data()
        for full_file_path in self.paths(file_config).paths__content():
            if full_file_path in content_files:
                return True
        return False

    # todo: this method should return a strongly typed class (ideally one from the file)
    def get_file_info(self, path : Safe_Str__File__Path                                        # Get file information (size, hash, etc.)
                       ) -> Optional[Dict[Safe_Id, Any]]:
        file = self.storage.file(path)
        if not file:
            return None

        content_size = int(file.metadata.content__size)                                # Get size from metadata
        return {Safe_Id("exists")       : True                                          ,
                Safe_Id("size")         : content_size                                  ,
                Safe_Id("content_hash") : file.metadata.content__hash                   ,
                Safe_Id("timestamp")    : file.metadata.timestamp                       ,
                Safe_Id("content_type") : file.config.file_type.content_type.value      }

    def list_files(self, prefix : Safe_Str__File__Path = None                                  # List all files, optionally filtered by prefix
                    ) -> List[Safe_Str__File__Path]:                                           # todo: see if we need this method
        if prefix is None:
            return list(self.storage.files__names())

        prefix_str = str(prefix)
        if not prefix_str.endswith('/'):
            prefix_str += '/'

        return [path for path in self.storage.files__names()
                if str(path).startswith(prefix_str)]

    def load(self, path : Safe_Str__File__Path                                                 # Load a file metadata from the given path
              ) -> Optional[Schema__Memory_FS__File]:
        return self.storage.file(path)

    def load_content(self, path : Safe_Str__File__Path                                         # Load raw content from the given path
                      ) -> Optional[bytes]:
        return self.storage.file__content(path)



    # todo: this should return a python object (and most likely moved into a Memory_FS__Stats class)
    def stats(self) -> Dict[Safe_Id, Any]:                                                     # Get file system statistics
        total_size = 0
        for path, content in self.storage.content_data().items():
            total_size += len(content)                                                          # todo: use the file size instead

        return {Safe_Id("type")            : Safe_Id("memory")               ,
                Safe_Id("file_count")      : len(self.storage.files       ()),
                Safe_Id("content_count")   : len(self.storage.content_data()),
                Safe_Id("total_size")      : total_size                      }
