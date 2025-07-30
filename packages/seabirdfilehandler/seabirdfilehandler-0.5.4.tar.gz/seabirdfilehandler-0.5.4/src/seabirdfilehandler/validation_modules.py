from collections import UserDict


class CnvValidationList(UserDict):
    """A python representation of the individual validation steps conducted
    in the process of a cnv file creation. These modules are stored in
    a dictionary structure, together with all the variables/metadata/etc.
    given in the header of a cnv file.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, cnv_header_val_modules: list):
        self.cnv_header_val_modules = cnv_header_val_modules
        self.data = {}
        self.modules = self.extract_individual_modules()
        for module in self.modules:
            module_data = self.create_dict_for_module(module)
            self.data[module] = module_data

    def extract_individual_modules(self) -> list:
        """ """
        module_list = []
        for line in self.cnv_header_val_modules:
            module = line.split("_")[0]
            if (module not in module_list) and (
                line.split()[0] != "file_type"
            ):
                module_list.append(module)
        return module_list

    def create_dict_for_module(self, module) -> dict:
        """

        Parameters
        ----------
        module :


        Returns
        -------

        """
        # TODO: probably need to split this into smaller bits
        out_dict = {}
        inner_action_dict = {}
        action_dict_present = False
        # extract lines corresponding to the module
        for line in self.cnv_header_val_modules:
            if module == line.split("_")[0]:
                # removing the module names from the lines
                shifting_index = len(module) + 1
                line_content = line[shifting_index:]
                # handle the case of the validation methods keyword being
                # 'action', which corresponds to an entire dict of values
                if line_content[:6] == "action":
                    action_dict_present = True
                    inner_action_dict = self.module_dict_feeder(
                        line_content[6:], inner_action_dict
                    )
                else:
                    # handle the cases where after some date value, another value
                    # is printed inside of [] brackets
                    double_value_list = line_content.split("[")
                    if len(double_value_list) > 1:
                        out_dict = self.module_dict_feeder(
                            double_value_list[1][shifting_index:-2], out_dict
                        )
                        line_content = double_value_list[0]
                    if line_content[:11] == "surface_bin":
                        surface_bin_dict = {}
                        for line in line_content.split(","):
                            self.module_dict_feeder(line, surface_bin_dict)
                        out_dict["surface_bin"] = surface_bin_dict
                        continue
                    # usual behavior, for 99% cases:
                    # assigning key and value to the module dict
                    out_dict = self.module_dict_feeder(line_content, out_dict)
        if action_dict_present:
            out_dict["action"] = inner_action_dict
        return out_dict

    def module_dict_feeder(
        self, line: str, dictionary: dict, split_value: str = "="
    ):
        """

        Parameters
        ----------
        line: str :

        dictionary: dict :

        split_value: str :
             (Default value = '=')

        Returns
        -------

        """
        # adds the values of a specific header line into a dictionary
        try:
            key, value = line.split(split_value)
        except ValueError:
            pass
        else:
            dictionary[key.strip()] = value.strip()
        finally:
            return dictionary

    def get(self, module: str) -> dict:
        """

        Parameters
        ----------
        module: str :


        Returns
        -------

        """
        for element in self.data:
            if str(element) == module:
                return self.data[element]
        else:
            return {}


class ValidationModule:
    """Class that is meant to represent the individual validation modules of
    the SeaSoft software. This includes all the input parameters and settins,
    as well as a description of the output.
    The idea is to inherit from this class for each individual module. But I
    am not sure if its worth the effort.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, name):
        self.name = name

    def extract_information(self):
        """ """
        pass
