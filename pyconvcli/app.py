import subprocess
import sys
import json
from pydash import map_, find, find_index,get, find_last
import tkinter.filedialog
import tkinter as tk
from tkinter import messagebox
import inspect
from .parse_classes import ParserArgType
from contextlib import redirect_stderr, redirect_stdout
import io
import shlex
import argparse


def build_options(cli):
    """Return a structure that allows us to build a cli application"""
    # delegate = EelDeligate.instance()
    # cli = delegate.cli
    start_key=find(cli.parsers.keys(),lambda key: key.find('.')==-1)
    # delegate.start_key=start_key
    json_version=build_sub_options(cli.parsers,start_key,cli)
    # string_version = json.dumps(json_version)
    return json_version

def find_longest_string_in_list(the_list):
    result=''
    for string_variable in the_list:
        if len(string_variable)>len(result):
            result=string_variable
    return result

def build_actions(parser,key,cli):
    actions=[]
    for action in parser['parser']._actions:
        if action.__class__.__name__=='PyconvCliCustomAction' or action.__class__.__name__=='_HelpAction':
            is_callable_parser=True
            action_descriptor = find_longest_string_in_list(action.option_strings)
            name = action_descriptor.replace('-','')
            actions.append(
                {
                    "name":name,
                    "key":key,
                    "call_key":key.replace(cli.root_module_name ,cli.entry_name,1),
                    "action_option":action_descriptor,
                    "action_nargs":parser['action_nargs'][name] if 'action_nargs' in parser and name in parser['action_nargs'] else 0
                }
            )
    return actions

def build_sub_options(parsers,key,cli):
    parser_object=parsers[key]
    choices=[]
    actions=[]
    if 'subparsers' in parser_object and hasattr(parser_object['subparsers'],'choices'):
        sub_keys=list(parser_object['subparsers'].choices.keys())
        for sub_key in sub_keys:
            child_key = '.'.join([key,sub_key])
            if child_key in parsers:
                sub_result = build_sub_options(parsers,child_key,cli)
                choices.append(sub_result)
    if 'callables' in parser_object:
        callables=parser_object['callables']
        for callable_key in callables:
            already_added_choice = find(choices, lambda choice:choice['name']==callable_key)
            if already_added_choice:
                already_added_choice['function_name']=callables[callable_key]['function_name']
                already_added_choice["callable_data"]=callables[callable_key]
            else:
                actions=build_actions(callables[callable_key],f'{key}.{callable_key}',cli)
                choices.append(
                    {
                        "name":callable_key,
                        "is_callable":True,
                        "key":key,
                        "call_key":key.replace(cli.root_module_name ,cli.entry_name,1),
                        "function_name":callables[callable_key]['function_name'],
                        "callable_data":callables[callable_key],
                        "actions":actions
                    }
                )
    is_callable_parser=False
    if parser_object['parser']._actions:
        actions=build_actions(parser_object,key,cli)
        is_callable_parser=len(actions)>0
    return {
        "name":key.split('.')[-1],
        "is_callable":is_callable_parser,
        "key":key,
        "call_key":key.replace(cli.root_module_name ,cli.entry_name,1),
        "choices":choices,
        "actions":actions
    }


class PyconvcliApp(tk.Frame):
    cli=None
    variables=[]
    def __init__(self, master,cli):
        self.cli=cli
        tk.Frame.__init__(self, master, padx=10,pady=10)
        self.options = build_options(cli)
        self.dropdown_map={}
        self.form_widgets={}
        self.usage=None

        text = tk.Label(master, text="Select a path from the dropdowns. When you hit a callable command it will give you more options")#tk.Text(master, height=1, font="TkDefaultFont 10")
        self.variable_a = tk.StringVar(self)
        self.variable_a.set(self.cli.entry_name)#options['name'])

        self.variable_a.trace('w', self.clear_to_root)
        self.variables=[self.variable_a]
        self.root_module_dd = tk.OptionMenu(self, self.variable_a, *[self.cli.entry_name])
        self.dropdown_map[str(self.variable_a)]=self.root_module_dd

        self.run_command_button = tk.Button(master, text ="Run Command", command = self.run_function)
        self.copy_command_button = tk.Button(master, text ="Copy Command to Clipboard", command = self.copy_command)


        text.pack(side=tk.TOP)
        self.root_module_dd.pack(side=tk.LEFT)
        # self.root_module_dd.configure(state='disabled')

        self.pack()
        self.update_options(str(self.variable_a))

    def clear_to_root(self, *args):
        self.clear_form_widgets()
        self.remove_variables(self.variables[1:])
        self.update_options(str(self.variable_a))

    def get_path_from_widgets(self):
        command_list = []
        action_included=False
        for item in self.form_widgets:
            variable_entry=self.form_widgets[item]['variable']

            if 'action' in self.form_widgets[item]:
                action = self.form_widgets[item]['action']
                variable_value = variable_entry.get()
                if variable_value:
                    command_list.append(f'--{item}')
                if action=="store_true" or action =='store_false' or action =='store_const':
                    continue
            if 'action_option' in self.form_widgets[item]:
                action_included=True
                action_nargs = self.form_widgets[item]['action_nargs']
                if action_nargs==0:
                    variable_value = variable_entry.get()
                    if variable_value:
                        command_list.append(f'--{item}')
                    continue
            if isinstance(variable_entry,list):
                list_of_values = map_(variable_entry,lambda value:value.get())
                if any(list_of_values):
                    command_list.append(f'--{item}')
                    for value in list_of_values:
                        if value:
                            command_list.append(value)
            else:
                value = self.form_widgets[item]['variable'].get()
                if value:
                    command_list.append(f'--{item}')
                    command_list.append(value)

        return (command_list,action_included)

    def run_function(self, *args, **kwargs):
        mapped_result=map_(self.variables,lambda variable:variable.get())
        if '' in mapped_result:
            mapped_result.remove('')
        sys.argv = mapped_result
        command_list,includes_actions = self.get_path_from_widgets()
        for command in command_list:
            sys.argv.append(command)
        args=[self.cli.entry_name ,*sys.argv[1:]]
        output=subprocess.run(args, capture_output=True)
        encoding='utf-8'
        if output.stderr:
            messagebox.showerror("Errors", '\n'.join(['Error!','Output:',output.stderr.decode(encoding)]))

        else:
            messagebox.showinfo("Success", f'Success!\n{output.stdout.decode(encoding)}')


    def copy_command(self):
        self.master.clipboard_clear()
        path_values = map_(self.variables,lambda variable:variable.get())[1:]
        if '' in path_values:
            path_values.remove('')
        command_list,includes_actions = self.get_path_from_widgets()
        sys.argv= [self.cli.root_module_name,*path_values, *command_list]
        for command in command_list:
            path_values.append(shlex.quote(command))
        with_entry = ' '.join([self.cli.entry_name,*path_values])

        std_out = io.StringIO()
        std_err = io.StringIO()
        with redirect_stdout(std_out):
            with redirect_stderr(std_err):
                try:
                    # If there are actions included we don't want people accidentally calling them on their machine because actions are called at parse time
                    if not includes_actions:
                        self.cli.parse_args()
                    self.master.clipboard_append(with_entry)
                    self.master.update()
                    label = tk.Label(self.master, text=f'"{with_entry}" copied to clipboard')
                    label.pack()
                    self.master.after(2000, lambda widget: widget.pack_forget(), label)
                    if includes_actions:
                        action_info = tk.Label(self.master, text=f'you have actions selected. actions run at parse time so to keep you from unintentionally running code we did not parse your params')
                        action_info.pack()
                        self.master.after(5000, lambda widget: widget.pack_forget(), action_info)
                except Exception as e:
                    messagebox.showerror("Errors", std_err.getvalue())
                except SystemExit as e:
                    the_err = std_err.getvalue()
                    the_out = std_out.getvalue()
                    if not the_err and the_out:
                        messagebox.showerror("Errors", the_out)
                    else:
                        messagebox.showerror("Errors", the_err)





    def get_selected_object(self):
        selected = self.options
        for variable in self.variables[1:]:
            selected = find(selected['choices'], lambda choice: choice['name'] == variable.get())
        return selected

    def remove_variables(self,context_to_remove):
        for variable in context_to_remove:
            dd_widget = self.dropdown_map[str(variable)]
            dd_widget.destroy()
            del self.dropdown_map[str(variable)]
            self.variables.remove(variable)


    def add_dropdown_option(self, selected_object):
        new_variable = tk.StringVar(self)
        new_variable.trace('w', self.update_options)
        new_option_menu = tk.OptionMenu(self, new_variable, *map_(selected_object["choices"],lambda item:item['name']))
        self.dropdown_map[str(new_variable)]=new_option_menu
        self.variables.append(new_variable)
        new_option_menu.pack(side=tk.LEFT)

    def add_another_arg(self,form_widget_object,choices=None,file_selector=None):

        variable = tk.StringVar()
        if file_selector:
            widget = tk.Button(form_widget_object['row'])
            widget.config(text="Browse Files", command=lambda : self.browse_files(variable,widget))
        elif choices:
            widget = tk.OptionMenu(form_widget_object['row'], variable, *choices)
        else:
            widget = tk.Entry(form_widget_object['row'],textvariable=variable)
        if not isinstance(form_widget_object['variable'],list):
            form_widget_object['variable']=[form_widget_object['variable'],variable]
        else:
            form_widget_object['variable'].append(variable)
        if not isinstance(form_widget_object['widget'],list):
            form_widget_object['widget']=[form_widget_object['widget'],widget]
        else:
            form_widget_object['widget'].append(widget)
        for widget in form_widget_object['widget']:
            widget.pack(side=tk.LEFT)
        form_widget_object['button'].pack(side=tk.RIGHT)

    def browse_files(self, variable, button):
        filename = tkinter.filedialog.askopenfilename(initialdir = "/", title = "Select a File",)
        if filename:
            variable.set(filename)
            button.config(text="Change File")


    def add_custom_annotated_field_to_form(self,key,param):
        key = key if len(param.annotation.args)==0 else param.annotation.args[0][2:]
        if "action" in param.annotation.kwargs:
            row = tk.Frame(self.master)
            variable = tk.IntVar()
            variable.set(0)
            self.form_widgets[key]={'variable':variable,
                                    'action':param.annotation.kwargs['action'],
                                    'widget':tk.Checkbutton(row, text=key, variable=variable),
                                    'row':row}
            row.pack()
            self.form_widgets[key]['widget'].pack()
            return



        if "nargs" in param.annotation.kwargs:
            if param.annotation.kwargs['nargs']=="*":
                row = tk.Frame(self.master)
                variable = tk.StringVar()
                choices_list_exists = "choices" in param.annotation.kwargs
                is_file_list = "type" in param.annotation.kwargs and param.annotation.kwargs['type'].__class__==argparse.FileType
                if is_file_list:
                    add_button_command = lambda : self.add_another_arg(self.form_widgets[key],file_selector=True)
                    widget = tk.Button(row)
                    widget.config(text="Browse Files", command=lambda : self.browse_files(variable,widget))
                elif choices_list_exists:
                    add_button_command = lambda : self.add_another_arg(self.form_widgets[key],param.annotation.kwargs['choices'])
                    widget = tk.OptionMenu(row, variable, *param.annotation.kwargs['choices'])
                else:
                    add_button_command = lambda : self.add_another_arg(self.form_widgets[key])
                    widget = tk.Entry(row,textvariable=variable)
                add_button = tk.Button(row, text ="add argument", command =add_button_command)

                self.form_widgets[key]={'variable':variable,
                                        'label':tk.Label(row,text=key),
                                        'widget':widget,
                                        'button':add_button,
                                        'row':row}
                row.pack()
                self.form_widgets[key]['label'].pack(side=tk.LEFT)
                self.form_widgets[key]['widget'].pack(side=tk.LEFT)
                add_button.pack(side=tk.RIGHT)
                return
            elif param.annotation.kwargs['nargs']>1:
                row = tk.Frame(self.master)
                variables=[]
                widgets=[]
                for i in range(param.annotation.kwargs['nargs']):
                    variable=tk.StringVar()
                    variables.append(variable)
                    choices_list_exists = "choices" in param.annotation.kwargs
                    is_file_list = "type" in param.annotation.kwargs and param.annotation.kwargs['type'].__class__==argparse.FileType
                    if is_file_list:
                        #Note the i=i int he parameter section is due to a context bug where the last button in the loop hijacks the others context if not provided in the params
                        # see https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments
                        widgets.append(tk.Button(row, name=f'file_open{i}',text="Browse Files", command=lambda i=i: self.browse_files(variables[i],widgets[i])))
                    elif choices_list_exists:
                        widgets.append(tk.OptionMenu(row, variable, *param.annotation.kwargs['choices']))
                    else:
                        widgets.append(tk.Entry(row,textvariable=variable))

                self.form_widgets[key]={'variable':variables,
                                        'label':tk.Label(row,text=key),
                                        'widget':widgets,
                                        'row':row}
                row.pack()
                self.form_widgets[key]['label'].pack(side=tk.LEFT)

                for widget in self.form_widgets[key]['widget']:
                    widget.pack(side=tk.LEFT)
                return
        if "type" in param.annotation.kwargs and param.annotation.kwargs['type'].__class__==argparse.FileType:
            row = tk.Frame(self.master)
            variable=tk.StringVar()

            button_explore = tk.Button(row)
            button_explore.config(text="Browse Files", command=lambda : self.browse_files(variable,button_explore))
            self.form_widgets[key]={'variable':variable,
                                    'label':tk.Label(row,text=key),
                                    'widget':button_explore,
                                    'row':row}

            self.form_widgets[key]['label'].pack(side=tk.LEFT)
            button_explore.pack()
            row.pack()
            return

        if "choices" in param.annotation.kwargs:
            row = tk.Frame(self.master)
            variable = tk.StringVar()
            self.form_widgets[key]={'variable':variable,
                                    'label':tk.Label(row,text=key),
                                    'widget':tk.OptionMenu(row, variable, *param.annotation.kwargs['choices']),
                                    'row':row}
            row.pack()
            self.form_widgets[key]['label'].pack(side=tk.LEFT)
            self.form_widgets[key]['widget'].pack(side=tk.RIGHT)
        else:
            row = tk.Frame(self.master)
            variable = tk.StringVar()
            self.form_widgets[key]={'variable':variable,
                                    'label':tk.Label(row,text=key),
                                    'widget':tk.Entry(row,textvariable=variable),
                                    'row':row}
            row.pack()
            self.form_widgets[key]['label'].pack(side=tk.LEFT)
            self.form_widgets[key]['widget'].pack(side=tk.RIGHT)

    def add_field_to_form(self,key,param,parser):
        if param.annotation.__class__==ParserArgType:
            self.add_custom_annotated_field_to_form(key,param)

        elif param.annotation==str or param.annotation==int:
            row = tk.Frame(self.master)
            variable = tk.StringVar()
            self.form_widgets[key]={'variable':variable,
                                    'label':tk.Label(row,text=key),
                                    'widget':tk.Entry(row, textvariable=variable),
                                    'row':row}
            row.pack()
            self.form_widgets[key]['label'].pack(side=tk.LEFT)
            self.form_widgets[key]['widget'].pack(side=tk.RIGHT)


    def clear_form_widgets(self):
        for item in self.form_widgets:
            for widget in self.form_widgets[item]:
                if widget!='variable' and widget!='action' and widget!='action_option' and widget!='action_name' and widget!='action_nargs':
                    value = self.form_widgets[item][widget]
                    if isinstance(value, list):
                        for form_widget in value:
                            try:
                                form_widget.destroy()
                            except AttributeError as e:
                                #likely destroy isn't an option so we'll got with pack_forget
                                form_widget.pack_forget()
                    else:
                        try:
                            self.form_widgets[item][widget].destroy()
                        except AttributeError as e:
                            #likely destroy isn't an option so we'll got with pack_forget
                            self.form_widgets[item][widget].pack_forget()
        self.form_widgets={}

    def getLastSelectedVariable(self):
        variable = find_last(self.variables, lambda variable: variable.get())
        return variable.get()

    def add_actions_to_form(self,callable_item):

        if 'actions' in callable_item:
            self.run_command_button.pack()
            self.copy_command_button.pack()
            if len(callable_item['actions'])>0:
                row = tk.Frame(self.master)
                actions_label=tk.Label(row, text="available actions:")
                actions_label.pack(side=tk.LEFT)
            for action in callable_item['actions']:

                self.form_widgets[action['name']]={'action_name':action['name'],
                                              'action_option':action['action_option'],
                                               'action_nargs':action['action_nargs'] if 'action_nargs' in action else 0,
                                              'row':row}
                nargs =  self.form_widgets[action['name']]['action_nargs']
                if nargs==0:
                    variable = tk.IntVar()
                    variable.set(0)
                    self.form_widgets[action['name']]['variable']=variable
                    self.form_widgets[action['name']]['widget']=tk.Checkbutton(row, text=action['action_option'], variable=variable)
                elif nargs=='*':
                    internal_frame = tk.Frame(row)
                    add_button_command = lambda key=action['name'] : self.add_another_arg(self.form_widgets[key])
                    add_entry_button=tk.Button(internal_frame, text ="add argument", command =add_button_command)
                    variable = tk.StringVar()
                    self.form_widgets[action['name']]['row']=internal_frame
                    self.form_widgets[action['name']]['label']=tk.Label(internal_frame, text=action['action_option'])
                    self.form_widgets[action['name']]['variable']=[variable]
                    self.form_widgets[action['name']]['widget']=[tk.Entry(internal_frame,textvariable=variable)]
                    self.form_widgets[action['name']]['button']=add_entry_button
                    self.form_widgets[action['name']]['label'].pack(side=tk.LEFT)
                    self.form_widgets[action['name']]['button'].pack(side=tk.RIGHT)
                    internal_frame.pack()
                else:
                    variable_list = []
                    widget_list = []
                    for index in range(nargs):
                        variable = tk.StringVar()
                        variable_list.append(variable)
                        widget_list.append(tk.Entry(row,textvariable=variable))
                    self.form_widgets[action['name']]['label']=tk.Label(row, text=action['action_option'])
                    self.form_widgets[action['name']]['variable']=variable_list
                    self.form_widgets[action['name']]['widget']=widget_list
                    self.form_widgets[action['name']]['label'].pack(side=tk.LEFT)
                row.pack()
                if isinstance(self.form_widgets[action['name']]['widget'],list):
                    for widget in self.form_widgets[action['name']]['widget']:
                        widget.pack(side=tk.LEFT)
                else:
                    self.form_widgets[action['name']]['widget'].pack(side=tk.LEFT)

    def display_help_text(self, parser):
        std_out = io.StringIO()
        with redirect_stdout(std_out):
            parser['parser'].print_help()
        self.usage=tk.Label(self.master, text=std_out.getvalue())
        self.usage.pack()

    def update_displayed_options(self,selected_object,changed_variable):
        if 'is_callable' in selected_object and selected_object['is_callable']:
            self.dropdown_map[str(changed_variable)].config(font='TkDefaultFont 20')
            if self.variables[-1].get():
                key='.'.join(map_(self.variables,lambda variable:variable.get())[:-1]).replace(self.cli.entry_name,self.cli.root_module_name,1)
                action_key='.'.join(map_(self.variables,lambda variable:variable.get())).replace(self.cli.entry_name,self.cli.root_module_name,1)
            else:
                key = '.'.join(map_(self.variables,lambda variable:variable.get())[:-2]).replace(self.cli.entry_name,self.cli.root_module_name,1)
                action_key = '.'.join(map_(self.variables,lambda variable:variable.get())[:-1]).replace(self.cli.entry_name,self.cli.root_module_name,1)
            if key in self.cli.parsers:
                parser = self.cli.parsers[key]
                last_selected_variable = self.getLastSelectedVariable()
                if 'callables' in parser and  last_selected_variable in parser['callables']:
                    callable_item =parser['callables'][self.getLastSelectedVariable()]
                if self.variables[-1].get() or 'function_name' in selected_object:
                    inspect_function = inspect.signature(get(callable_item['class_ref'],callable_item['function_name']))
                    self.run_command_button.pack()
                    self.copy_command_button.pack()
                    for key in inspect_function.parameters:
                        if key!='self':
                            self.add_field_to_form(key,inspect_function.parameters[key],parser)
            if action_key in self.cli.parsers:
                parser = self.cli.parsers[action_key]
            else:
                parser = parser['callables'][self.getLastSelectedVariable()]
            self.add_actions_to_form(selected_object)

            self.display_help_text(parser)
    def update_options(self, *args):
        self.run_command_button.pack_forget()
        self.copy_command_button.pack_forget()
        if self.usage:
            self.usage.pack_forget()
            self.usage=None
        if len(self.form_widgets)>0:
            self.clear_form_widgets()
        self.master.geometry('')

        changed_variable=None
        for variable in self.variables:
            if str(variable)==args[0]:
                changed_variable=variable
                break
        if changed_variable == find_last(self.variables,lambda varaible: variable.get()) :
            selected_object=self.get_selected_object()
            if selected_object and "choices" in selected_object:
                self.dropdown_map[str(changed_variable)].config(font='TkDefaultFont')
                self.add_dropdown_option(selected_object)
            self.update_displayed_options(selected_object,changed_variable)



        else:
            context_to_remove = self.variables[find_index(self.variables,lambda variable:variable==changed_variable)+1:]

            self.remove_variables(context_to_remove)
            selected_object=self.get_selected_object()
            if selected_object and "choices" in selected_object:
                self.add_dropdown_option(selected_object)
            self.update_displayed_options(selected_object,changed_variable)



