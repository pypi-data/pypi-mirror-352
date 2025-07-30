from memory_fs.file.Memory_FS__File                         import Memory_FS__File
from memory_fs.schemas.Schema__Memory_FS__File__Type        import Schema__Memory_FS__File__Type
from osbot_utils.type_safe.decorators.type_safe             import type_safe
from osbot_utils.helpers.Safe_Id                            import Safe_Id
from osbot_utils.decorators.methods.cache_on_self           import cache_on_self
from memory_fs.Memory_FS                                    import Memory_FS
from memory_fs.project.Schema__Memory_FS__Project__Config   import Schema__Memory_FS__Project__Config, Schema__Memory_FS__Project__Path_Strategy
from osbot_utils.type_safe.Type_Safe                        import Type_Safe

class Memory_FS__Project(Type_Safe):
    config: Schema__Memory_FS__Project__Config

    def file(self, file_id     : Safe_Id,
                   path_strategy: Schema__Memory_FS__Project__Path_Strategy,
                   file_type    : Schema__Memory_FS__File__Type
              ) -> Memory_FS__File:

        file_paths = []
        for path_handler in path_strategy.path_handlers:
            file_path = path_handler().generate_path()
            file_paths.append(file_path)

        with Memory_FS__File() as file:
            with file.file_config as _:
                _.file_type  = file_type
                _.file_paths = file_paths
                _.file_id  = file_id
            return file

    @cache_on_self
    def memory_fs(self):
        storage   = self.config.storage()
        memory_fs = Memory_FS(storage=storage)
        return memory_fs

    @type_safe
    def path_strategy(self, path_strategy_name:Safe_Id) -> Schema__Memory_FS__Project__Path_Strategy:
        return self.config.path_strategies.get(path_strategy_name)
