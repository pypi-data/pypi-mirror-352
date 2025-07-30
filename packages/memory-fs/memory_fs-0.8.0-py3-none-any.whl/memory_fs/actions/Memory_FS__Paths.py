from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.actions.Memory_FS__File_Name             import Memory_FS__File_Name
from osbot_utils.type_safe.decorators.type_safe         import type_safe
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

# todo:
#  content to be saved as {file_id}.{extension}
#  ".fs.json" to be saved as {file_id}.{extension}.config
#  metatada to be saved as {file_id}.{extension}.metadata

class Memory_FS__Paths(Type_Safe):
    file__config: Schema__Memory_FS__File__Config

    @cache_on_self
    def file_name(self):
        return Memory_FS__File_Name(file__config=self.file__config)

    @type_safe
    def paths(self):
        full_file_paths = []
        if self.file__config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in self.file__config.file_paths:
                full_file_path = self.file_name().config__for_path(file_path)
                full_file_paths.append(full_file_path)
        else:
            full_file_path = self.file_name().config__for_path()
            full_file_paths.append(full_file_path)

        return full_file_paths

    def paths__content(self) -> Safe_Str__File__Path:
        full_file_paths = []
        full_file_name = self.file_name().content()
        if self.file__config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in self.file__config.file_paths:
                content_path = self.file_name().content__for_path(file_path)
                full_file_paths.append(content_path)
        else:
            full_file_paths.append(Safe_Str__File__Path(full_file_name))

        return full_file_paths