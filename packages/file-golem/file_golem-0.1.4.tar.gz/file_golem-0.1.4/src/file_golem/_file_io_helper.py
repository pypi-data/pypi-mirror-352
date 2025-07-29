import os
import pydoc
from file_golem.file_datatypes import FileDatatypes

############### FILE IO ####################
def _does_path_exist(path):
    return os.path.exists(path)


def _locate_class(object_class):
    model_type = pydoc.locate(object_class)
    if model_type is None:
        raise Exception(f'Could not find model class {object_class}')
    return model_type


def _initialize_load_save_extension_dicts(supported_datatypes):
    load_function_dict = {}
    save_function_dict = {}
    file_extension_dict = {}

    can_load_all = (len(supported_datatypes) == 0)
    if (FileDatatypes.OMEGA_CONF.value in supported_datatypes) or can_load_all:

        from omegaconf import OmegaConf
        def _load_omega_conf(path):
            config = OmegaConf.load(path)
            return config

        def _save_omega_conf(data,path):
            OmegaConf.save(data,path)


        load_function_dict[FileDatatypes.OMEGA_CONF] = _load_omega_conf
        save_function_dict[FileDatatypes.OMEGA_CONF] = _save_omega_conf
        file_extension_dict[FileDatatypes.OMEGA_CONF] = 'yaml'

    if (FileDatatypes.MATPLOTLIB.value) in supported_datatypes or can_load_all:
        import matplotlib.pyplot as plt

        def _save_matplotlib(data,path):
            plt.savefig(path,bbox_inches='tight', pad_inches =0.0,format='pdf')

        save_function_dict[FileDatatypes.MATPLOTLIB] = _save_matplotlib
        file_extension_dict[FileDatatypes.MATPLOTLIB] = 'pdf'


    if (FileDatatypes.NUMPY.value in supported_datatypes) or can_load_all:
        import numpy as np
        def _load_np(path):
            return np.load(path)
        
        def _save_np(data,path):
            np.save(path,data)

        load_function_dict[FileDatatypes.NUMPY] = _load_np
        save_function_dict[FileDatatypes.NUMPY] = _save_np
        file_extension_dict[FileDatatypes.NUMPY] = 'npy'

    if (FileDatatypes.PANDAS.value in supported_datatypes) or can_load_all:
        import pandas as pd
        def _save_pd(data,path):
            data.to_csv(path)
        
        def _load_pd(path):
            return pd.read_csv(path)
        
        load_function_dict[FileDatatypes.PANDAS] = _load_pd
        save_function_dict[FileDatatypes.PANDAS] = _save_pd
        file_extension_dict[FileDatatypes.PANDAS] = 'csv'
    
    if (FileDatatypes.JSON.value in supported_datatypes) or can_load_all:
        import json
        def _load_json(path):
            with open(path, 'r') as f:
                return json.load(f)
            
        def _save_json(json_data,path):
            with open(path, 'w') as f:
                json.dump(json_data, f, indent=4)
        
        load_function_dict[FileDatatypes.JSON] = _load_json
        save_function_dict[FileDatatypes.JSON] = _save_json
        file_extension_dict[FileDatatypes.JSON] = 'json'

    if (FileDatatypes.TEXT.value in supported_datatypes) or can_load_all:
        def _load_txt(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            print("CAM WUZ HERE: ", content)
            return content

        def _save_txt(data, file_path):
            with open(file_path, 'w') as file:
                file.write(data)

        load_function_dict[FileDatatypes.TEXT] = _load_txt
        save_function_dict[FileDatatypes.TEXT] = _save_txt
        file_extension_dict[FileDatatypes.TEXT] = 'txt'

    if (FileDatatypes.TORCH.value in supported_datatypes) or can_load_all:
        import torch
        def _save_torch(data,path):
            torch.save(data,path)
        def _load_torch(path,weights_only=False):
            if torch.cuda.is_available():
                return torch.load(path,weights_only=weights_only)
            else:
                return torch.load(path,weights_only=weights_only,map_location=torch.device('cpu'))
        
        load_function_dict[FileDatatypes.TORCH] = _load_torch
        save_function_dict[FileDatatypes.TORCH] = _save_torch
        file_extension_dict[FileDatatypes.TORCH] = 'pt'

    if (FileDatatypes.PICKLE.value in supported_datatypes) or can_load_all:
        import pickle
        def _save_pickle(data,path):
            with open(path, 'wb') as f:
                pickle.dump(data, f)

        def _load_pickle(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
            
        load_function_dict[FileDatatypes.PICKLE] = _load_pickle
        save_function_dict[FileDatatypes.PICKLE] = _save_pickle
        file_extension_dict[FileDatatypes.PICKLE] = 'pkl'

    if (FileDatatypes.PNG.value in supported_datatypes) or can_load_all:
        import imageio
        def _load_png(path):
            return imageio.imread(path)
        def _save_png(data,path):
            with open(path, 'wb') as img_file:
                img_file.write(data)
        load_function_dict[FileDatatypes.PNG] = _load_png
        save_function_dict[FileDatatypes.PNG] = _save_png
        file_extension_dict[FileDatatypes.PNG] = 'png'

    if (FileDatatypes.PDF.value in supported_datatypes) or can_load_all:
        import matplotlib.pyplot as plt
        def _save_plt_fig(path):
            plt.savefig(path,bbox_inches='tight', pad_inches =0.0,format='pdf')
            plt.close()

        save_function_dict[FileDatatypes.PDF] = _save_plt_fig
        file_extension_dict[FileDatatypes.PDF] = 'pdf'

    if (FileDatatypes.SHELL.value in supported_datatypes) or can_load_all:
        def _save_shell_script(data,path):
            with open(path, 'w') as f:
                f.write(data)
            os.chmod(path, 0o755)
        
        save_function_dict[FileDatatypes.SHELL] = _save_shell_script
        file_extension_dict[FileDatatypes.SHELL] = 'sh'

    if (FileDatatypes.SLURM_SCRIPT.value in supported_datatypes) or can_load_all:
        def _save_slurm_script(data,path):
            with open(path, 'w') as f:
                f.write(data)
            os.chmod(path, 0o755)
        
        save_function_dict[FileDatatypes.SLURM_SCRIPT] = _save_slurm_script
        file_extension_dict[FileDatatypes.SLURM_SCRIPT] = 'sh'

    if (FileDatatypes.SLURM_OUTPUT_STD.value in supported_datatypes) or can_load_all:
        file_extension_dict[FileDatatypes.SLURM_OUTPUT_STD] = 'out'

    if (FileDatatypes.SLURM_OUTPUT_ERR.value in supported_datatypes) or can_load_all:
        file_extension_dict[FileDatatypes.SLURM_OUTPUT_ERR] = 'err'

    return load_function_dict,save_function_dict,file_extension_dict