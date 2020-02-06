"""
@author: The KnowEnG dev team
lanier4@illinois.edu
sobh@illinois.edu

"""
import os
import warnings
import sys
# import pandas as pd
# from pandas.io.common import EmptyDataError
import yaml

sys.path.insert(1, '../src')
import yaml_utility as yamut

from IPython.display import display
import ipywidgets as widgets

import knpackage.toolbox as kn

YAML_TAB_STRING = ' ' * 5

TRUE_STRINGS = ['True', 'true', 1]
FALSE_STRINGS = ['False', 'false', 0]
NONE_STRINGS = ['none', 'None']

#                                                                                       set default file types
PARAMETER_FILE_TYPES = ['.yml', '.txt']
USER_DATAFILE_EXTENSIONS_LIST = ['.tsv', '.txt', '.df', '.gz', '.csv']

#                                                                                       layout styles
lisbox_layout                  = widgets.Layout(width='50%')
box_layout = widgets.Layout(display='inline-flex',
                            flex_flow='row',
                            justify_content='space-between',
                            align_items='stretch',
                            border='none',
                            width='100%')


def get_progress_bar(run_parameters):
    """ Usage: run_parameters = get_progress_bar(run_parameters) # displays progress bar & returns handle key

    Args:
         run_parameters:    python dict of key: value pairs

    Returns:
        run_parameters:     with progress_bar key pointer to a (displayed) widgets.IntProgress bar
    """
    max_count = run_parameters['num_iteration']
    run_parameters['progress_bar'] = widgets.IntProgress(
        value=7,
        min=0,
        max=max_count,
        step=1,
        description='Loading',
        bar_style='success', # 'success', 'info', 'warning', 'danger' or ''
        orientation='horizontal'
    )
    display(run_parameters['progress_bar'])  # display the bar

    return run_parameters


def get_run_parameters_html_table(run_parameters, show_list=None):
    """ formatting for widgets.html_table

    Args:
        run_parameters:
        show_list:

    Returns:
        html_table:     the run_parameters formatted as an html <table>...
    """
    orderd_keys = sorted(run_parameters.keys())
    html_table = '<table>\n'
    for k in orderd_keys:
        if show_list is None or k in show_list:
            html_table += '\t<tr><td>%35s: </td> <td> %45s</td></tr>\n'%(k, run_parameters[k])
    html_table += '</table>'

    return html_table


def get_run_parameters(run_file_name):
    """ get the run parameters from the full file name """
    run_parameters = None
    try:
        with open(run_file_name, 'r') as file_handle:
            run_parameters = yaml.load(file_handle)
    except:
        try:
            import knpackage.toolbox as kn
            run_dir, run_file = os.path.split(run_file_name)
            run_parameters = kn.get_run_parameters(run_dir, run_file)
        except:
            pass
        pass
    finally:
        if run_parameters is None:
            run_parameters = {}

    return run_parameters


def std_out_run_parameters_str(run_parameters, std_output=True):
    """ static function to display run_parameters dict to command line or cell output

    Args:
         run_parameters:
         std_output:

    Returns:
        run_parameters_string:  run_parameters formatted as     centered: strings
    """
    run_parameters_string = ''

    # determine the length of the longest key string:
    left_string_length = 1
    for k in run_parameters.keys():
        if len(k) > left_string_length:
            left_string_length = len(k)
    # construct the formatting string
    format_string = '%s%i%s: %s' % ('%', left_string_length + 1, 's', '%s')

    # construct the output string by iteration through the dict
    keys_list = sorted(list(run_parameters.keys()))
    for k in keys_list:
        v = run_parameters[k]
        if std_output == True:
            print(format_string % (k, v))
        run_parameters_string += format_string % (k, v) + '\n'
    return run_parameters_string


def run_parameters_to_string(run_pars, prefix_string=''):
    """ yaml format writable dictionary string used by _save_parameters

    Args:
         run_pars:          python dict
         prefix_string:     for inset where key refers to another dict

    Returns:
         run_pars_string:   the run parameters as a yaml file writable string
    """
    max_key_length = 2
    for k in run_pars.keys():
        if len(k) > max_key_length:
            max_key_length = len(k)
    max_key_length += 5

    keys_list = sorted(list(run_pars.keys()))
    run_pars_string = ''
    for k in keys_list:
        v = run_pars[k]
        key_padding = (max_key_length - len(k)) * ' '
        if isinstance(v, int):
            v_str = '%i' % (v)
        elif isinstance(v, float):
            v_str = '%f' % (v)
        elif isinstance(v, str):
            v_str = v
        elif isinstance(v, dict):
            v_str = run_parameters_to_string(v, prefix_string=YAML_TAB_STRING)
        else:
            v_str = str(v)

        run_pars_string += prefix_string + k + ':' + key_padding + v_str + '\n'

    return run_pars_string


def user_data_list(target_dir, FEXT):
    """ user_file_list = update_user_data_list(user_data_dir, FEXT)

    Args:
        target_dir:     directory to list
        FEXT:           File extension list e.g. ['.tsv', '.txt']
    Returns:
        my_file_list:   the list of files with the specified prefixes
    """
    my_file_list = []
    for f in os.listdir(target_dir):
        if os.path.isfile(os.path.join(target_dir, f)):
            noNeed, f_ext = os.path.splitext(f)
            if f_ext in FEXT:
                my_file_list.append(f)
            else:
                print(f)

    if len(my_file_list) <= 0:
        my_file_list.append('No Data')

    return my_file_list


VIEW_BUTTON_NAME_DEFAULTS = {'show': 'Show', 'hide':'Hide'}
PARS_EDIT_BUTTON_NAME_SET = {'edit': 'Edit', 'set': 'Set'}
PARS_ADD_BUTTON_NAME_SET = {'new': 'New Parameter', 'add': 'Add'}

YAML_FILE_SELECT_LABEL = 'Select Parameters File'
PARAMETERS_EDITOR_LABEL = 'Parameters Edit by Key - Value'

NO_DATA_DICTIONARY = {'No Input': 'No Data'}

class ParameterSetWidgets():
    """ Set of widgets to select, edit, access and save a .yml file of key: value pairs as python dict
    (no directly accessable parameters)

    methods:
        obj = ParameterSetWidgets(input_data_dir, file_types)
        obj.show_controls()
        obj.get_selected_file_name()
        obj.get_edited_run_parameters()
        obj.cell_display_run_parameters()

    private-ish methods:            ( may change state of object )
        _add_parameter(self, button)
        _delete_selected_parameter(self, button)
        _edit_parameter(self, button)
        _hide_html_parameters(self)
        _key_value_change(self, dropdown)
        _open_run_parameters(self, run_directory, run_file)
        _save_parameters(self, button)
        _set_run_parameters(self, button)
        _show_html_parameters(self)
        _update_controls_run_parameters(self, parameters_dictionary)
        _view_all(self, button)

    TODO:   add refresh key to yaml files list
    """
    def __init__(self, input_data_dir=None, file_types=PARAMETER_FILE_TYPES):
        """ Constructor: create all control widgets with no-parameters state

        Args:
            self:                   implicitly construct self
            input_data_dir:         valid directory name with appropriate permissions
            file_types:             list of acceptable file types e.g. ['.yml', '.txt']

        Returns:
            self:                   controls instantiated with controls displayed flag set False
                                    --                                             to display, call self.show_controls()
        """
        if os.path.isdir(input_data_dir) == True:
            self.input_data_dir = input_data_dir
        else:
            self.input_data_dir = os.getcwd()

        # TOP                                                        self.select_file_button "owns" self...file_selector
        self.select_file_button = widgets.Button(description='Select-Revert', disabled=False,
                                                 button_style='', tooltip='show | hide selected file')

        options = user_data_list(self.input_data_dir, file_types)
        options.append('Refresh')
        self.select_file_button.file_selector = widgets.Dropdown(options=options,description='', layout=lisbox_layout)
        self.select_file_button.file_selector.file_types = file_types
        self.select_file_button.file_selector.data_directory = input_data_dir
        self.select_file_button.on_click(self._set_run_parameters)

        # MIDDLE                   self.ed_par_button "owns" the parameters,  self...key_selector &  self...parameter_ed
        parameters_dictionary = NO_DATA_DICTIONARY
        self._input_dir_name = None
        self._input_file_name = None

        self.ed_par_button = widgets.Button(description=PARS_EDIT_BUTTON_NAME_SET['edit'],
                                            disabled=False,
                                            button_style='',
                                            tooltip='show | hide selected file')
        self.del_par_button = widgets.Button(description='delete',
                                            disabled=True,
                                            button_style='',
                                            tooltip='delete selected parameter')
        self.del_par_button.on_click(self._delete_selected_parameter)

        keys_list = sorted(list(parameters_dictionary.keys()))
        self.ed_par_button.parameters = {k: parameters_dictionary[k] for k in keys_list}
        text_list = list(self.ed_par_button.parameters.values())
        self.ed_par_button.key_selector = widgets.Dropdown(options=keys_list,
                                                           value=str(keys_list[0]),
                                                           description='')
        self.ed_par_button.key_selector.observe(self._key_value_change, 'value')
        self.ed_par_button.parameter_ed = widgets.Text(options=text_list,
                                                       value=str(text_list[0]),
                                                       placeholder='Type something',
                                                       description='',
                                                       disabled=True)
        self.ed_par_button.on_click(self._edit_parameter)
        self.show_run_parameters_button = widgets.Button(description=VIEW_BUTTON_NAME_DEFAULTS['show'],
                                                         disabled=False,
                                                         button_style='',
                                                         tooltip='Show | Hide all parameters')
        self.show_run_parameters_button.on_click(self._view_all)

        # BOTTOM                                                                     instantiate Save, Show|Hide buttons
        self.save_run_parameters_button = widgets.Button(description='Save',
                                                         disabled=True,
                                                         button_style='',
                                                         tooltip='Save run parameters')
        self.save_run_parameters_button.on_click(self._save_parameters)

        self.add_parameter_button = widgets.Button(description=PARS_ADD_BUTTON_NAME_SET['new'],
                                                         disabled=True,
                                                         button_style='',
                                                         tooltip='Save run parameters')
        self.add_parameter_button.on_click(self._add_parameter)
        self.add_parameter_button.new_parameter = widgets.Text(value='None',
                                                              placeholder='Type something',
                                                              description='',
                                                              disabled=True)

        self.all_parameters_view_box = widgets.HTML(value='No Data', placeholder='',description='')

        # TOP                                                                                     package widget set TOP
        self.ed_par_button.file_select_label = widgets.Label(value=YAML_FILE_SELECT_LABEL)
        self.yaml_file_selector = widgets.VBox([self.ed_par_button.file_select_label,
                                                widgets.HBox([self.select_file_button.file_selector,
                                                              self.select_file_button],
                                                             layout=box_layout)] )
        # MIDDLE                                                                               package widget set MIDDLE
        self.select_file_button.parameter_edit_label = widgets.Label(value=PARAMETERS_EDITOR_LABEL)
        self.parameters_editor = widgets.VBox([self.select_file_button.parameter_edit_label,
                                               widgets.HBox([self.ed_par_button.key_selector,
                                                             self.del_par_button,
                                                             self.ed_par_button.parameter_ed,
                                                             self.ed_par_button], layout=box_layout) ])

        # BOTTOM                                                                               package widget set BOTTOM
        self.view_save_buttons = widgets.HBox([self.save_run_parameters_button,
                                               self.add_parameter_button.new_parameter,
                                               self.add_parameter_button,
                                               self.show_run_parameters_button],
                                              layout=box_layout)
        self.show_save_box = widgets.VBox([self.view_save_buttons, self.all_parameters_view_box])

        #                                                                           set a FLAG - show_controls only once
        self._controls_displayed = False

    def _update_controls_run_parameters(self, parameters_dictionary):
        """ reset the controls run_parameters """
        #                                       replace this objects parameters and display the keys
        keys_list = sorted(list(parameters_dictionary.keys()))
        self.ed_par_button.parameters = {k: parameters_dictionary[k] for k in keys_list}
        self.ed_par_button.key_selector.options = keys_list
        #                                       # replace & display the values options
        key_value = keys_list[0]
        self.ed_par_button.key_selector.value = key_value
        text_list = list(self.ed_par_button.parameters.values())
        self.ed_par_button.parameter_ed.options = text_list
        self.ed_par_button.parameter_ed.value = str(self.ed_par_button.parameters[key_value])

        if self.show_run_parameters_button.description == VIEW_BUTTON_NAME_DEFAULTS['hide']:
            # show the full set of parameters, and reset the Show_All | Hide button to Hide state (enabled)
            self._show_html_parameters()
        self.show_run_parameters_button.disabled = False
        self.add_parameter_button.disabled = False

    def _add_parameter(self, button):
        """ callback for self.add_parameter_button """
        if self.add_parameter_button.description == PARS_ADD_BUTTON_NAME_SET['new']:
            self.add_parameter_button.description = PARS_ADD_BUTTON_NAME_SET['add']
            self.add_parameter_button.new_parameter.disabled = False
        else:
            self.add_parameter_button.description = PARS_ADD_BUTTON_NAME_SET['new']
            self.add_parameter_button.new_parameter.disabled = True
            new_parameter_key = self.add_parameter_button.new_parameter.value
            if new_parameter_key in ['None', 'none']:
                return
            run_parameters = self.ed_par_button.parameters
            run_parameters[new_parameter_key] = None
            self._update_controls_run_parameters(run_parameters)
            self.ed_par_button.key_selector.value = new_parameter_key
            self.save_run_parameters_button.disabled = False
            self.add_parameter_button.new_parameter.value = 'None'

    def _delete_selected_parameter(self, button):
        """ callback for self.del_par_button

        """
        key_to_delete = self.ed_par_button.key_selector.value
        run_parameters = self.ed_par_button.parameters
        if len(run_parameters) == 1:
            run_parameters = NO_DATA_DICTIONARY
            self.del_par_button.disabled = True
        else:
            del(run_parameters[key_to_delete])

        self._update_controls_run_parameters(run_parameters)
        self.save_run_parameters_button.disabled = False

    def show_controls(self):
        """ display controls below jupyter notebook cell where called
        Args:
             self:              initialized set of controls with or without valid directory/filename or parameters
        Returns:
            self:               with controls displayed flag set True
        """
        if self._controls_displayed == True:
            return
        display(self.yaml_file_selector)
        # display(self.select_file_button.view_box)
        display(self.parameters_editor)
        display(self.show_save_box)
        self._controls_displayed = True

    def get_selected_file_name(self):
        """ read the file name from the select file dropdown self.select_file_button.file_selector
        Args:
            self:               .select_file_button.file_selector
                                .select_file_button.data_directory
        Returns:
            full_file_name:     suitable for opening   --   else None
        """
        if self.select_file_button.file_selector.value == 'Refresh':
            options = user_data_list(self.input_data_dir, self.select_file_button.file_selector.file_types)
            options.append('Refresh')
            self.select_file_button.file_selector.options = options
            self.select_file_button.file_selector.value = self.select_file_button.file_selector.options[0]

        full_file_name = os.path.join(self.select_file_button.file_selector.data_directory,
                                      self.select_file_button.file_selector.value)

        if not os.path.isfile(full_file_name):
            full_file_name = None

        return full_file_name

    def _set_run_parameters(self, button):
        """ open the selected file and set this object's run_parameters into the display
        Args:
            self:               self.select_file_button      --     callback for "Select"
        Returns:
            self:               ._input_dir_name, _input_file_name,
                                .ed_par_button.parameters, & all children
        """
        directory_name = self.select_file_button.file_selector.data_directory
        file_name = self.select_file_button.file_selector.value
        if os.path.isfile(os.path.join(directory_name, file_name)):
            try:
                #                                       opening the parameters validates the selected dir & name
                parameters_dictionary                   = self._open_run_parameters(directory_name, file_name)
                #                                       set description to "hide" to show_all
                self.show_run_parameters_button.description = VIEW_BUTTON_NAME_DEFAULTS['hide']
                self._update_controls_run_parameters(parameters_dictionary)
                self._input_dir_name                    = directory_name
                self._input_file_name                   = file_name

                # #                                       replace this objects parameters and display the keys
                # keys_list                               = sorted(list(parameters_dictionary.keys()))
                # self.ed_par_button.parameters           = {k: parameters_dictionary[k] for k in keys_list}
                # self.ed_par_button.key_selector.options = keys_list
                # #                                       # replace & display the values options
                # key_value                               = keys_list[0]
                # self.ed_par_button.key_selector.value   = key_value
                # text_list                               = list(self.ed_par_button.parameters.values())
                # self.ed_par_button.parameter_ed.options = text_list
                # self.ed_par_button.parameter_ed.value   = str(self.ed_par_button.parameters[key_value])
                #
                # # show the full set of parameters, and reset the Show_All | Hide button to Hide state (enabled)
                # self._show_html_parameters()
                # self.show_run_parameters_button.description = VIEW_BUTTON_NAME_DEFAULTS['hide']
                # self.show_run_parameters_button.disabled = False

                self.save_run_parameters_button.disabled = True
                self.del_par_button.disabled = False

            except:
                #                                       fail by resetting object to uninitialized state
                parameters_dictionary                   = {'No Input': 'No Data'}
                self.ed_par_button.parameters           = parameters_dictionary
                self._input_dir_name                    = None
                self._input_file_name                   = None

                # Hide the full set of parameters, and reset the Show_All | Hide button to Show_All (disabled)
                self._hide_html_parameters()
                self.show_run_parameters_button.description = VIEW_BUTTON_NAME_DEFAULTS['show']
                self.show_run_parameters_button.disabled = True
                pass

    def _key_value_change(self, dropdown):
        """ callback for self.ed_par_button.key_selector (observe value change)
        Args:
             self:          .ed_par_button    all children
             dropdown:      self.ed_par_button.key_selector   --    observe value callback
        Returns:
            self:           self.ed_par_button                --    children reset
        """
        key_value = self.ed_par_button.key_selector.value
        par_value = self.ed_par_button.parameters[key_value]
        self.ed_par_button.parameter_ed.value = str(par_value)
        self.ed_par_button.description = PARS_EDIT_BUTTON_NAME_SET['edit']
        self.ed_par_button.parameter_ed.disabled = True

    def _edit_parameter(self, button):
        """ Callback for self.ed_par_button == "Edit" / "Set" Button

        Args:
             self:      this object
             button:    self.ed_par_button = widgets.Button    "Edit" / "Set"

        Returns:
            self:       this object with "Edit" "Set" reset to opposite and
                        self.all_parameters_view_box.value updated if
                        self.show_run_parameters_button.description set "Hide" (e.g. do show now)
        """
        if button.description == PARS_EDIT_BUTTON_NAME_SET['edit']:
            button.description                          = PARS_EDIT_BUTTON_NAME_SET['set']
            button.parameter_ed.disabled                = False
        else:
            button.description                          = PARS_EDIT_BUTTON_NAME_SET['edit']
            key_value                                   = button.key_selector.value
            text_value                                  = button.parameter_ed.value
            self.ed_par_button.parameters[key_value]    = text_value
            text_list                                   = list(self.ed_par_button.parameters.values())
            self.ed_par_button.parameter_ed.options     = text_list
            button.parameter_ed.disabled                = True
            #                                           Update the parameters display if currently showing
            if self.show_run_parameters_button.description == VIEW_BUTTON_NAME_DEFAULTS['hide']:
                self._show_html_parameters()
            self.save_run_parameters_button.disabled = False

    def _view_all(self, button):
        """ "Show_All" / "Hide" Callback

        Args:
            self:           ._show_html_parameters()
            button:         .show_run_parameters_button

        Returns:
            self:           self.all_parameters_view_box.value       --     either cleared or displayed
        """
        if self.show_run_parameters_button.description == VIEW_BUTTON_NAME_DEFAULTS['show']:
            button.description = VIEW_BUTTON_NAME_DEFAULTS['hide']
            self._show_html_parameters()
        else:
            button.description = VIEW_BUTTON_NAME_DEFAULTS['show']
            self._hide_html_parameters()

    def _show_html_parameters(self):
        """ self.all_parameters_view_box        -- Fill """
        self.all_parameters_view_box.value = get_run_parameters_html_table(self.ed_par_button.parameters)

    def _hide_html_parameters(self):
        """ self.all_parameters_view_box        -- Clear """
        self.all_parameters_view_box.value = ''

    def get_edited_run_parameters(self):
        """ get the ordered run parameters as held by self.ed_par_button  """
        keys_list = sorted(list(self.ed_par_button.parameters.keys()))
        return {k: self.ed_par_button.parameters[k] for k in keys_list}

    def cell_display_run_parameters(self):
        """ print formatted dict to std out """
        std_out_run_parameters_str(self.ed_par_button.parameters, std_output=True)

    def _save_parameters(self, button):
        """ "Save" Callback
        Args:
             self:
             button:            self.save_run_parameters_button Save
        """
        #                                   get the edited parameters from the controls
        run_parameters      = self.get_edited_run_parameters()
        run_pars_string     = run_parameters_to_string(run_parameters)

        #                                   compose the output file name
        if 'SaveTo_directory' in run_parameters:
            directory_name  = run_parameters['AA-SaveTo_directory']
        else:
            directory_name = os.getcwd()
        if 'AA-SaveAs_file_name' in run_parameters:
            file_name   = kn.create_timestamped_filename(run_parameters['AA-SaveAs_file_name'], name_extension='yml')
        else:
            file_name   = kn.create_timestamped_filename(self._input_file_name, name_extension='yml')

        #                                   fearlessly write the file
        full_file_name = os.path.join(directory_name, file_name)
        with open(full_file_name, 'w') as fd:
            fd.write(run_pars_string)

    def _open_run_parameters(self, run_directory, run_file):
        """ Read run directory name and run_file into a dictionary

        Args:
            self:               private function
            run_directory:      directory where run_file is expected.
            run_file:           run_parameters file   ('.yml')
        Returns:
            run_parameters:     python dictionary of name - value parameters.
        """
        run_file_name = os.path.join(run_directory, run_file)
        with open(run_file_name, 'r') as file_handle:
            run_parameters = yaml.load(file_handle)

        #                                                   establish ouput file name for save function
        _, run_file_core_name = os.path.split(run_file_name)
        run_file_core_name, _ = os.path.splitext(run_file_core_name)
        file_name = kn.create_timestamped_filename(run_file_core_name, name_extension='yml')
        run_parameters['AA-SaveAs_file_name'] = file_name
        if self._input_dir_name is None or os.path.isdir(self._input_dir_name) == False:
            run_parameters['AA-SaveTo_directory'] = run_directory
        else:
            run_parameters['AA-SaveTo_directory'] = self._input_dir_name

        return run_parameters

class SpreadsheetDataObject():
    """ spreadsheet as object of analysis sdo = SpreadsheetDataObject('/home/mydir/spreadsheet_df)
    1)  spreadsheet condition:  nans, unique index and columns, duplicate rows, columns, type consistanecy,...
    2)  available analysis:     methods and pipelines determined by the spreadsheet condition
    3)  output available:       graphical, tabular, numerical ranking
    """
    def __init__(self, spreadsheet_name_full_path=None):
        """ . """
        self.spreadsheet_name_full_path = spreadsheet_name_full_path

ignore_columns_list = ['cluster_ip_address', 'cluster_shared_ram',
                       'cluster_shared_volumn', 'processing_method',
                       'parallelism', 'run_directory', 'tmp_directory']

class SelectViewRunWidget():
    """  """
    def __init__(self, callback_function, selection_directory='run_dir', results_dir='run_dir/results'):
        """  """
        warnings.filterwarnings('ignore')

        self.selection_directory = selection_directory
        self.results_dir = results_dir
        self.callback_function = callback_function

        if os.path.isdir(self.results_dir) == False:
            os.makedirs(self.results_dir)

        self.filename_selector      = widgets.Dropdown(options=user_data_list(self.selection_directory,
                                                                              FEXT=PARAMETER_FILE_TYPES),
                                                       description='', layout=lisbox_layout)

        self.show_parameters_button     = widgets.Button(description=VIEW_BUTTON_NAME_DEFAULTS['show'],
                                                     disabled=False, button_style='',
                                                     tooltip='show | hide parameters')
        self.show_parameters_button.on_click(self._toggle_view_run_parameters)

        self.view_parameters_box    = widgets.HTML(value="", description="")

        self.run_button             = widgets.Button(description='Run',
                                                     disabled=False)
        self.run_button.on_click(self._open_parameters_and_run_callback_function)

        # Package for display                                                                     package the widget set
        self.button_set_html_header = widgets.HTML(value='')
        self.view_save_buttons = widgets.VBox([self.button_set_html_header,
                                               widgets.HBox([self.filename_selector,
                                                             self.show_parameters_button,
                                                             self.run_button],
                                                            layout=box_layout), self.view_parameters_box])

        display(self.view_save_buttons)
        self._display_yaml_df()


    def _display_yaml_df(self):
        run_files_df = yamut.get_yaml_df(self.selection_directory)
        columns_list = list(run_files_df.columns)
        display_list = []
        for col_name in columns_list:
            if col_name in ignore_columns_list:
                continue
            display_list.append(col_name)

        self.button_set_html_header.value = run_files_df[display_list].to_html()


    def _open_parameters_and_run_callback_function(self, button):
        self.run_button.disabled = True
        run_file_name = os.path.join(self.selection_directory, self.filename_selector.value)
        run_parameters = get_run_parameters(run_file_name)
        run_parameters['output_dir'] = self.results_dir

        self.callback_function(run_parameters)

        self.run_button.disabled = False


    def _toggle_view_run_parameters(self, button):
        if self.show_parameters_button.description == VIEW_BUTTON_NAME_DEFAULTS['show']:
            self.show_parameters_button.description = VIEW_BUTTON_NAME_DEFAULTS['hide']
            # open the selected file,
            run_file_name = os.path.join(self.selection_directory, self.filename_selector.value)
            run_parameters = get_run_parameters(run_file_name)

            # get_run_parameters_html_table(run_paramters)
            run_parameters_html = get_run_parameters_html_table(run_parameters)

            # display the html_table in the view parameters box
            self.view_parameters_box.value = run_parameters_html
        else:
            self.show_parameters_button.description = VIEW_BUTTON_NAME_DEFAULTS['show']
            self.view_parameters_box.value = ''

def get_html_page():
    return '<!doctype html><html><head><body><p>"Hello HTML"</p></body></head></html>'





























