from file_golem.file_datatypes import FileDatatypes, FilePathEntries, AbstractDatatype

class Config(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.OMEGA_CONF
    GRID_IDX = 'grid_idx'

    RELATIVE_PATH_TUPLE = (
        FilePathEntries.CONFIG_ENTRY,
        {FilePathEntries.CUSTOM_LOGIC: '_grid_search_suffix'}
    )
    
    @staticmethod
    def _grid_search_suffix(data_args):
        if not (Config.GRID_IDX in data_args):
            return ()
        
        idx = '_'.join(map(str, data_args[Config.GRID_IDX]))
        return tuple([idx])
