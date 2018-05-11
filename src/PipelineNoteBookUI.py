"""
@author: The KnowEnG dev team
lanier4@illinois.edu
sobh@illinois.edu

"""
import os
import pandas as pd
from pandas.io.common import EmptyDataError
import yaml

from IPython.display import display
import ipywidgets as widgets

import knpackage.toolbox as kn

YAML_TAB_STRING = ' ' * 5

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
    """ Usage: run_parameters = get_progress_bar(run_parameters) """
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
    """ for widgets.
    html_table = get_run_parameters_html_table(run_parameters)
    """
    orderd_keys = sorted(run_parameters.keys())
    html_table = '<table>\n'
    for k in orderd_keys:
        if show_list is None or k in show_list:
            html_table += '\t<tr><td>%35s: </td> <td> %45s</td></tr>\n'%(k, run_parameters[k])
    html_table += '</table>'

    return html_table


def std_out_run_parameters_str(run_parameters, std_output=True):
    """ static function to display run_parameters dict to command line or cell output """
    run_parameters_string = ''
    left_string_length = 1
    for k in run_parameters.keys():
        if len(k) > left_string_length:
            left_string_length = len(k)

    format_string = '%s%i%s: %s' % ('%', left_string_length + 1, 's', '%s')

    keys_list = sorted(list(run_parameters.keys()))
    for k in keys_list:
        v = run_parameters[k]
        if std_output == True:
            print(format_string % (k, v))
        else:
            run_parameters_string += format_string % (k, v) + '\n'

    return run_parameters_string


def run_parameters_to_string(run_pars, prefix_string=''):
    """ yaml format writable dictionary string
    Args:
         run_pars:          python dict
         prefix_string:     for inset where key refers to another dict
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
    """
    # print('target_dir = ', target_dir)
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

VIEW_BUTTON_NAME_DEFAULTS = {'show': 'Show_All', 'hide':'Hide'}
PARS_EDIT_BUTTON_NAME_SET = {'edit': 'Edit', 'set': 'Set'}

class ParameterSetWidgets():
    """ pending improvements:
    1 Add | Remove Key-Value button in middle of Save - Show_All

    2 IF  - Edit button is clicked when key-value is in USER_DATAFILE_EXTENSIONS_LIST
            - change control logic in edit_parameter
        - Select (file) is retargeted to user_data directory
            - self.select_file_button.file_selector.data_directory changes
        - Select moves file name to key-value
            - set_run_parameters as callback for self.select_file_button needs switching function
        - Set updates the parameter
            - - change control logic in edit_parameter
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

        #                                                            self.select_file_button "owns" self...file_selector
        self.select_file_button = widgets.Button(description='Select', disabled=False,
                                                 button_style='', tooltip='show | hide selected file')
        # self.select_file_button.view_box = widgets.HTML(value="", description="")
        self.select_file_button.file_selector = widgets.Dropdown(options=user_data_list(self.input_data_dir, file_types),
                                                                 description='', layout=lisbox_layout)
        self.select_file_button.file_selector.data_directory = input_data_dir
        self.select_file_button.on_click(self.set_run_parameters)
        self.yaml_file_selector = widgets.Box([self.select_file_button.file_selector, self.select_file_button],
                                              layout=box_layout)

        #                          self.ed_par_button "owns" the parameters,  self...key_selector &  self...parameter_ed
        parameters_dictionary = {'No Input': 'No Data'}
        self._input_dir_name = None
        self._input_file_name = None
        self.ed_par_button = widgets.Button(description=PARS_EDIT_BUTTON_NAME_SET['edit'],
                                            disabled=False,
                                            button_style='',
                                            tooltip='show | hide selected file')
        keys_list = sorted(list(parameters_dictionary.keys()))
        self.ed_par_button.parameters = {k: parameters_dictionary[k] for k in keys_list}
        text_list = list(self.ed_par_button.parameters.values())
        self.ed_par_button.key_selector = widgets.Dropdown(options=keys_list,
                                                           value=str(keys_list[0]),
                                                           description='')
        self.ed_par_button.key_selector.observe(self._key_value_change, 'value')
        key_value = self.ed_par_button.key_selector.value
        value_text = str(parameters_dictionary[key_value])
        self.ed_par_button.parameter_ed = widgets.Text(options=text_list,
                                                       value=str(text_list[0]),
                                                       placeholder='Type something',
                                                       description='',
                                                       disabled=True)
        self.ed_par_button.on_click(self.edit_parameter)
        self.show_run_parameters_button = widgets.Button(description=VIEW_BUTTON_NAME_DEFAULTS['show'],
                                                         disabled=False,
                                                         button_style='',
                                                         tooltip='Show | Hide all parameters')
        self.show_run_parameters_button.on_click(self._view_all)

        #                                                                            instantiate Save, Show|Hide buttons
        self.save_run_parameters_button = widgets.Button(description='Save',
                                                         disabled=False,
                                                         button_style='',
                                                         tooltip='Save run parameters')
        self.save_run_parameters_button.on_click(self._save_parameters)
        self.all_parameters_view_box = widgets.HTML(value='No Data', placeholder='',description='')

        #                                                                                  package the three widget sets
        self.view_save_buttons = widgets.Box([self.save_run_parameters_button, self.show_run_parameters_button],
                                              layout=box_layout)
        self.parameters_editor = widgets.HBox([self.ed_par_button.key_selector,
                                               self.ed_par_button.parameter_ed,
                                               self.ed_par_button], layout=box_layout)
        self.show_save_box = widgets.VBox([self.view_save_buttons, self.all_parameters_view_box])
        #          set flag S.T. show_controls will only show once
        self._controls_displayed = False

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
        full_file_name = os.path.join(self.select_file_button.file_selector.data_directory,
                                      self.select_file_button.file_selector.value)

        if not os.path.isfile(full_file_name):
            full_file_name = None

        return full_file_name

    def set_run_parameters(self, button):
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
                self._input_dir_name                    = directory_name
                self._input_file_name                   = file_name
                #                                       replace this objects parameters and display the keys
                keys_list                               = sorted(list(parameters_dictionary.keys()))
                self.ed_par_button.parameters           = {k: parameters_dictionary[k] for k in keys_list}
                self.ed_par_button.key_selector.options = keys_list
                #                                       # replace & display the values options
                key_value                               = keys_list[0]
                self.ed_par_button.key_selector.value   = key_value
                text_list                               = list(self.ed_par_button.parameters.values())
                self.ed_par_button.parameter_ed.options = text_list
                self.ed_par_button.parameter_ed.value   = str(self.ed_par_button.parameters[key_value])
            except:
                #                                       fail by resetting object to uninitialized state
                parameters_dictionary                   = {'No Input': 'No Data'}
                self.ed_par_button.parameters           = parameters_dictionary
                self._input_dir_name                    = None
                self._input_file_name                   = None
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

    def edit_parameter(self, button):
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
            file_name   = kn.create_timestamped_filename(run_parameters['AA-SaveAs_file_name'], name_extension='.yml')
        else:
            file_name   = kn.create_timestamped_filename(self._input_file_name, name_extension='.yml')

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
        file_name = kn.create_timestamped_filename(run_file, name_extension='.yml')
        run_parameters['AA-SaveAs_file_name'] = file_name
        run_parameters['AA-SaveTo_directory'] = run_directory

        return run_parameters
