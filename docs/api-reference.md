API Reference
=============

suricate
--------

### **`api_is_ready()`**

### **`debuglog(message, *args)`**

### **`expand_variables(value, variables=None, window=None)`**

### **`extract_variables(window=None, append_suricate_variables=True)`**

### **`get_setting(key, default=None)`**

### **`get_variable(key, default=None)`**

### **`is_packaged()`**

### **`load_settings()`**

### **`log(message, *args)`**

### **`reload_module(module)`**

### **`set_debuglog(active=None)`**

Suricate.lib.datetimeutil
-------------------------

### **`continue_serie(edit, view)`**

### **`get_times(tstring=None)`**

Return a list of the different formats available for tstring, see
"time_formats" on settings file. If tstring is None, use current
time.

### **`time_to_clipboard(view=None)`**

Suricate.lib.dictionaries
-------------------------

### **`switch_language(view)`**

Suricate.lib.docs
-----------------

Basic tools to parse python files and generate documentation.

### **`folder(path, parents=[])`**

### **`import_module(module_name)`**

### **`markdown(items, level=1, indent=0, indentstr='  ')`**

### **`module(module_name, metaname=None)`**

Retrieve information of module's routines. Note: the module is
reloaded.

### **`routine(funcobj)`**

Retrieve signature as string of funcobj.

### **`to_buffer(title, modules)`**

### **`to_buffer_(title, root)`**

Suricate.lib.duckduckgo
-----------------------

Search on DuckDuckGo

### **`get_answer(query, scope=None, **kwargs)`**

### **`insert_answer(edit, view, event=None)`**

### **`show_popup(view, event=None, css_file=None, scope_regex=None, **kwargs)`**

Suricate.lib.iniquickpanel
--------------------------

### **`insert(view, ini_file, section)`**

Suricate.lib.latex
------------------

### **`clean(window=None)`**

Remove LaTeX temporary files.

### **`convert_to_tex(string)`**

Convert special characters to TeX symbols.

### **`launch_pdf(window=None)`**

Launch PDF associated with view.

### **`paragraph_to_tex(edit, view)`**

Convert special characters in paragraph to TeX symbols.

Suricate.lib.navigator
----------------------

### **`exclude_patterns(exclude_binaries)`**

Return a pair of callable objects that matches any exclude pattern in
global settings, for folders and files respectively.

### **`launch(mode='open', view=None)`**

Open navigator quick panel.

  * `mode=='open'` Open selected file with Sublime Text
  * `mode=='launch'` Try to externally launch selected file

Suricate.lib.osutil
-------------------

### **`executable(path)`**

### **`toggle_read_only(path)`**

### **`which(name, flags=1)`**

Return the full path to the first executable found in the environmental
variable PATH matching the given name.

Suricate.lib.popup_util
-----------------------

Handy wrappers around sublime pop-up API.

### **`get_css(view)`**

### **`score(lhs, rhs)`**

Suricate.lib.process
--------------------

### **`async(*args, **kwargs)`**

Launch a new process and wait for output asynchronously.
Calls popen_print_output.

### **`popen(cmd, working_dir=None, shell=None, timeout=None)`**

Wrapper around subprocess.Popen. Launch a new process and wait timeout
seconds for output. Return stdout, stderr.

### **`popen_print_output(*args, **kwargs)`**

Launch a new process and wait for output; show status message when
finished and print stdout to Sublime's console. Show an error dialogue if
something printed to stderr. Calls popen.

### **`spawn(cmd, working_dir=None, shell=None)`**

Spawn a new process

### **`startfile(path)`**

Try to emulate the behaviour of double-clicking the file.

### **`touch(paths, times=None)`**

Suricate.lib.profiles
---------------------

### **`add()`**

### **`find_profiles()`**

### **`print_commands(commands, indentation=4, minsep=10)`**

### **`remove()`**

### **`to_buffer()`**

Suricate.lib.searchbar
----------------------

Search online

### **`search_selection(view, event=None, engine=None)`**

### **`show(view, window, caption=None, engine=None)`**

Suricate.lib.settings
---------------------

Commands to manage settings files. `settings_file` should include a file name
and extension, but not a path. If none is given, use the default Suricate
settings file.

### **`append_value_to_array(key, value, settings_file=None)`**

Append value to key in settings_file.

### **`load_save_settings(*args, **kwds)`**

Context manager to load and save settings.

### **`set_from_resources(key, patterns, settings_file=None, set_mode='file', window=None)`**

Set the key in settings_file from a list of resources found based on
patterns. Available values for `set_mode`:

  * "file": `Packages/Default/Preferences.sublime-settings`
  * "file_name": `Preferences.sublime-settings`
  * "file_base_name": `Preferences`


### **`set_key_value(key, value, settings_file=None)`**

Set value for key in settings_file.

### **`toggle_boolean(key, settings_file=None)`**

Toggle the value of key in settings_file.

Suricate.lib.sublime_wrapper
----------------------------

Handy wrappers around sublime API.

### **`copy_build_variable_to_clipboard(key=None, window=None)`**

If key is None, show a quick panel with the currently available build
variables.

### **`execute(window=None, **kwargs)`**

Runs an external process asynchronously. On Windows, GUIs are suppressed.
``exec`` is the default command used by build systems, thus it provides
similar functionality. However, a few options in build systems are taken
care of by Sublime Text internally so they list below only contains
parameters accepted by this command.

  * cmd ``[String]``
  * file_regex ``String``
  * line_regex ``String``
  * working_dir ``String``
  * encoding ``String``
  * env ``{String: String}``
  * path ``String``
  * shell ``Bool``
  * kill ``Bool``: If True will simply terminate the current build process.
  This is invoked via Build: Cancel command from the Command Palette.
  * quiet ``Bool``: If True prints less information about running the
  command.

### **`flush_to_buffer(text, name=None, scratch=False, syntax=None, syntax_file=None)`**

Flush text to a new buffer.

### **`foreach_region(func, edit, view, clear=False)`**

Replace each selected region by the result of applying func on that
region. If clear, move the cursor to the end of each region.

### **`get_selection(view=None)`**

Retrieve selected regions as a list of strings.

### **`insert(string, edit, view, clear=False)`**

Insert string replacing view's current selection. If clear, move the
cursor to the end of each region.

### **`locate_and_load_resource(hint)`**

Try to load the first match of hint

### **`paste_build_variable(edit, key=None, view=None, window=None)`**

If key is None, show a quick panel with the currently available build
variables.

### **`show_quick_panel(display_list, on_done, window=None)`**

Show a quick panel fed with display_list on window. on_done must be a
callable object that accepts one argument, the element picked (not the
index!). It won't be called if the user cancels.

Suricate.lib.text
-----------------

### **`complete_line(line, max_line_length, tab_width, char=None)`**

Returns a string of `char` that together with `line` sums
`max_line_length` characters. If `char` is `None` use `line`'s last
character.

### **`fill_current_line(edit, view, max_line_length=None, char=None)`**

@todo It doesn't work as expected, rewrite.

### **`get_max_line_length(view, guess)`**

### **`line_length(line, tab_width)`**

### **`randomize(edit, view)`**

### **`split_current_line(edit, view, max_line_length=None)`**

### **`split_line(line, max_line_length)`**

@todo Only splits on spaces.

Suricate.lib.thirdparty
-----------------------

Suricate.lib.thirdparty.duckduckgo2html
---------------------------------------

Retrieve results from the DuckDuckGo zero-click API in simple HTML format.

### **`results2html(results, results_priority=None, max_number_of_results=None, ignore_incomplete=True, always_show_related=False, header_start_level=1, hide_headers=False, hide_signature=False)`**

### **`search(query, useragent='duckduckgo2html', **kwargs)`**

Suricate.lib.vcs
----------------

### **`call(cmd, active_flags, view)`**

### **`get_commands(active_flags, path)`**

### **`show_quick_panel(path=None)`**

Suricate.lib.vcs_parser
-----------------------

Parse output of different version control systems.
Usage example: git status | python {file} status git

### **`parse(out, command, vcsname)`**

Returns a list of pairs `[filepath, extra information]`.
