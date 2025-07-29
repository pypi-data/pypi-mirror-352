from osbot_utils.type_safe.decorators.type_safe         import type_safe
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

#  ".fs.json" to be saved as {file_id}.config
#  metatada to be saved as {file_id}.metadata

class Memory_FS__Paths(Type_Safe):

    @type_safe
    def paths(self, file_config: Schema__Memory_FS__File__Config):
        full_file_paths = []
        full_file_name = Safe_Str__File__Path(f"{file_config.file_id}.{file_config.file_type.file_extension}")
        if file_config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in file_config.file_paths:
                content_path   = Safe_Str__File__Path(f"{file_path}/{full_file_name}")
                full_file_path = Safe_Str__File__Path(content_path + ".fs.json")         # todo: refactor this into a better location

                full_file_paths.append(full_file_path)
        else:
            full_file_paths.append(Safe_Str__File__Path(full_file_name + ".fs.json"))   # todo: fix the use of this hard-coded + ".fs.json"

        return full_file_paths

    def paths__content(self, file_config: Schema__Memory_FS__File__Config):
        full_file_paths = []
        full_file_name = Safe_Str__File__Path(f"{file_config.file_id}.{file_config.file_type.file_extension}")
        if file_config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in file_config.file_paths:
                content_path   = Safe_Str__File__Path(f"{file_path}/{full_file_name}")
                full_file_paths.append(content_path)
        else:
            full_file_paths.append(full_file_name)

        return full_file_paths