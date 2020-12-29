import sys
import json
from pydash import map_, find, find_index,get
import tkinter as tk
from tkinter import messagebox
import inspect
from .parse_classes import ParserArgType
from contextlib import redirect_stderr, redirect_stdout
import io


def build_options(cli):
    """Return a structure that allows us to build a cli application"""
    # delegate = EelDeligate.instance()
    # cli = delegate.cli
    start_key=find(cli.parsers.keys(),lambda key: key.find('.')==-1)
    # delegate.start_key=start_key
    json_version=build_sub_options(cli.parsers,start_key)
    string_version = json.dumps(json_version)
    return json_version

def build_sub_options(parsers,key):
    parser_object=parsers[key]
    choices=[]
    if 'subparsers' in parser_object and hasattr(parser_object['subparsers'],'choices'):
        sub_keys=list(parser_object['subparsers'].choices.keys())
        for sub_key in sub_keys:
            child_key = '.'.join([key,sub_key])
            if child_key in parsers:
                sub_result = build_sub_options(parsers,child_key)
                choices.append(sub_result)
    if 'callables' in parser_object:
        callables=parser_object['callables']
        for callable_key in callables:
            choices.append(
                {
                    "name":callable_key,
                    "is_callable":True,
                    "key":key,
                    "function_name":callables[callable_key]['function_name']
                }
            )
    return {
        "name":key.split('.')[-1],
        "is_callable":False,
        "key":key,
        "choices":choices
    }



class TinkerDelegate(tk.Frame):
    cli=None
    entry_word=None
    variables=[]
    def __init__(self, master,cli):
        self.cli=cli
        tk.Frame.__init__(self, master, padx=10,pady=10)
        self.options = build_options(cli)
        self.dropdown_map={}
        self.form_widgets={}
        self.usage=None


        self.dict = {'Asia': ['Japan', 'China', 'Malaysia'],
                     'Europe': ['Germany', 'France', 'Switzerland']}
        text = tk.Text(master, height=1)
        text.insert(tk.INSERT, "Select the path for your command")
        self.variable_a = tk.StringVar(self)
        self.variable_b = tk.StringVar(self)
        self.variable_a.set(self.options['name'])
        self.variables=[self.variable_a,self.variable_b]
        # self.optionmenu_a = tk.OptionMenu(self, self.variable_a,'')
        self.optionmenu_b = tk.OptionMenu(self, self.variable_b, *map_(self.options["choices"],'name'))
        self.dropdown_map[str(self.variable_b)]=self.optionmenu_b
        self.variable_b.trace('w', self.update_options)
        self.run_command_button = tk.Button(master, text ="Run Command", command = self.run_function)
        self.copy_command_button = tk.Button(master, text ="Copy Command to Clipboard", command = self.copy_command)

        text.config(state=tk.DISABLED)
        text.pack()

        # self.optionmenu_a.pack()
        self.optionmenu_b.pack(side=tk.LEFT)
        # self.run_command_button.pack()
        # self.copy_command_button.pack()

        self.pack()


    def run_function(self, *args, **kwargs):
        sys.argv=map_(self.variables,lambda variable:variable.get())
        for item in self.form_widgets:
            variable_entry=self.form_widgets[item]['variable']
            if isinstance(variable_entry,list):
                list_of_values = map_(variable_entry,lambda value:value.get())
                if any(list_of_values):
                    sys.argv.append(f'--{item}')
                    for value in list_of_values:
                        if value:
                            sys.argv.append(value)
            else:
                value = self.form_widgets[item]['variable'].get()
                if value:
                    sys.argv.append(f'--{item}')
                    sys.argv.append(value)

        # with StdoutFake() as faked_stdout:
        std_err = io.StringIO()
        std_out = io.StringIO()
        with redirect_stderr(std_err):
            with redirect_stdout(std_out):
                try:
                    self.cli.run()
                    messagebox.showinfo("Ran without errors", std_out.getvalue())
                except Exception as e:
                    messagebox.showerror("Errors", e)
                except SystemExit as e:
                    messagebox.showerror("Errors", std_err.getvalue())

    def copy_command(self):
        self.master.clipboard_clear()
        path_values = map_(self.variables,lambda variable:variable.get())[1:]
        for item in self.form_widgets:
            variable_entry=self.form_widgets[item]['variable']
            if isinstance(variable_entry,list):
                list_of_values = map_(variable_entry,lambda value:value.get())
                if any(list_of_values):
                    path_values.append(f'--{item}')
                    for value in list_of_values:
                        if value:
                            path_values.append(value)
            else:
                value = self.form_widgets[item]['variable'].get()
                if value:
                    path_values.append(f'--{item}')
                    path_values.append(value)
        with_entry = ' '.join([self.cli.entry_name,*path_values])
        sys.argv=[self.cli.root_module_name,*path_values]

        std_err = io.StringIO()
        with redirect_stderr(std_err):
            try:
                self.cli.parse_args()
                self.master.clipboard_append(with_entry)
                self.master.update()
                label = tk.Label(self.master, text=f'"{with_entry}" copied to clipboard')
                label.pack()
                self.master.after(2000, lambda widget: widget.pack_forget(), label)
            except Exception as e:
                messagebox.showerror("Errors", std_err.getvalue())
            except SystemExit as e:
                messagebox.showerror("Errors", std_err.getvalue())





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

    def printarsandkwargs(self,*args,**kwargs):
        print(args,kwargs)
        for variable in self.variables:
            if str(variable)==args[0]:
                print(variable.get())

    def add_dropdown_option(self, selected_object):
        new_variable = tk.StringVar(self)
        new_variable.trace('w', self.update_options)
        new_option_menu = tk.OptionMenu(self, new_variable, *map_(selected_object["choices"],'name'))
        self.dropdown_map[str(new_variable)]=new_option_menu
        self.variables.append(new_variable)
        new_option_menu.pack(side=tk.LEFT)

    def add_another_arg(self,form_widget_object):
        variable = tk.StringVar()
        widget = tk.Entry(form_widget_object['row'],textvariable=variable)
        if not isinstance(form_widget_object['variable'],list):
            form_widget_object['variable']=[form_widget_object['variable'],variable]
        else:
            form_widget_object['variable'].append(variable)
        if not isinstance(form_widget_object['widget'],list):
            form_widget_object['widget']=[form_widget_object['widget'],widget]
        else:
            form_widget_object['widget'].append(variable)
        widget.pack(side=tk.RIGHT)
        form_widget_object['button'].pack(side=tk.RIGHT)



    def add_custom_annotated_field_to_form(self,key,param):
        key = key if len(param.annotation.args)==0 else param.annotation.args[0][2:]
        if "nargs" in param.annotation.kwargs:
            if param.annotation.kwargs['nargs']=="*":
                #ToDo handle a button to add more arg entries as requested
                row = tk.Frame(self.master)
                variable = tk.StringVar()
                add_button = tk.Button(row, text ="add argument", command = lambda : self.add_another_arg(self.form_widgets[key]))

                self.form_widgets[key]={'variable':variable,
                                        'label':tk.Label(row,text=key),
                                        'widget':tk.Entry(row,textvariable=variable),
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
                    widgets.append(tk.Entry(row,textvariable=variable))

                self.form_widgets[key]={'variable':variables,
                                        'label':tk.Label(row,text=key),
                                        'widget':widgets,
                                        'row':row}
                row.pack()
                self.form_widgets[key]['label'].pack(side=tk.LEFT)
                for widget in self.form_widgets[key]['widget']:
                    widget.pack(side=tk.RIGHT)
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

    def add_field_to_form(self,key,param):
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
        print(key,param)

    def clear_form_widgets(self):
        for item in self.form_widgets:
            for widget in self.form_widgets[item]:
                if widget!='variable':
                    value = self.form_widgets[item][widget]
                    if isinstance(value, list):
                        for form_widget in value:

                                form_widget.destroy()

                            # form_widget.pack_forget()
                    else:
                        self.form_widgets[item][widget].destroy()
                        # self.form_widgets[item][widget].pack_forget()
        self.form_widgets={}

    def update_options(self, *args):

        if self.usage:
            self.usage.pack_forget()
            self.usage=None
        if len(self.form_widgets)>0:
            self.clear_form_widgets()
        self.master.geometry('')
        print(args)
        changed_variable=None
        for variable in self.variables:
            if str(variable)==args[0]:
                changed_variable=variable
                break
                print(variable.get())
        if changed_variable == self.variables[-1]:
            selected_object=self.get_selected_object()
            if selected_object and "choices" in selected_object:
                self.add_dropdown_option(selected_object)
            else:
                if 'is_callable' in selected_object and selected_object['is_callable']:
                    print(self.dropdown_map[str(changed_variable)].config().keys())
                    self.dropdown_map[str(changed_variable)].config(font='TkDefaultFont 20')
                    key = '.'.join(map_(self.variables,lambda variable:variable.get())[:-1])
                    if key in self.cli.parsers:
                        parser = self.cli.parsers[key]
                        callable_item =parser['callables'][self.variables[-1].get()]
                        inspect_function = inspect.signature(get(callable_item['class_ref'],callable_item['function_name']))
                        self.run_command_button.pack()
                        self.copy_command_button.pack()
                        for key in inspect_function.parameters:
                            if key!='self':
                                self.add_field_to_form(key,inspect_function.parameters[key])
                        std_out = io.StringIO()
                        with redirect_stdout(std_out):
                            callable_item['parser'].print_help()
                        self.usage=tk.Label(self.master, text=std_out.getvalue())
                        self.usage.pack()


        else:
            context_to_remove = self.variables[find_index(self.variables,lambda variable:variable==changed_variable)+1:]
            print(context_to_remove)
            self.run_command_button.pack_forget()
            self.copy_command_button.pack_forget()
            self.remove_variables(context_to_remove)
            selected_object=self.get_selected_object()
            if selected_object and "choices" in selected_object:
                self.add_dropdown_option(selected_object)



