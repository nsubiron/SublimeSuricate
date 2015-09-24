Quick Guide
===========

Sublime Text's Suricate is a command framework for [Sublime Text 3]. It provides
an easier way to implement simple commands to extend Sublime Text functionality
without the need to create a new plugin for it. This guide aims to provide a
quick overview on how _Suricate commands_ work and how to start writing your own
commands.

## Profiles

_Suricate Profiles_ are JSON files containing definitions of commands. A couple
of profiles come already shipped and active by default with Sublime Suricate. To
activate a profile add it to your **profile list** via _"Suricate: Add Profile"_
in the command palette (`ctrl+shift+p`). To deactivate it use _"Suricate: Remove
Profile"_. Alternatively, you can edit your profile list by hand in your
"User/Suricate.sublime-settings".

When a profile is active all the files matching "ProfileName.suricate-profile"
within your Packages directory are loaded (just as any other Sublime Text
settings file) and the Suricate merges their commands and adds them to your user
profile. To take a look at your user profile use _"Suricate: View Profiles"_.
This generates a list of your active commands as well as lists for each
individual profile found in your packages directory tree. Take into account that
the commands active in your user profile are not necessarily available in
Sublime Text, whether or not a command can be used depends on the set of flags
given by the command definition. These flags are updated in a per-view basis and
they may be active or not depending on things as current platform, whether the
current buffer exists on disk or if it is under a source control system as git
or svn.

## Commands

A typical Suricate command is defined as follows

```json
"open_windows_terminal_here":
{
  "caption":      "Open Terminal Here...",
  "keys":         ["ctrl+o", "ctrl+t"],
  "flags":        "Windows|IsFile",
  "call":         "Suricate.lib.process.spawn",
  "args":         {"cmd": ["start", "cmd.exe"], "working_dir": "${file_path}"},
  "context_menu": true
}
```

This creates a command entry in the command palette, in the context menu and
assigns a key binding to it. Moreover, the flags specify that the command is
only active on Windows and when the current buffer is a file existing on disk.

When triggered, this command calls the function `spawn()` inside the Python
module `Suricate.lib.process` with the arguments given in "args". The "call" tag
can be set to any python module that can be imported within Sublime Text's
Python interpreter, in this case the module is defined in
"Packages/Suricate/lib/process.py".

### User Commands

Any of the fields above can be overridden adding a suricate-profile file
to your User folder, e.g. let's say that the previous command resides in
"ProfileName.suricate-profile" inside the Suricate package, and you want to
assign a different key binding and perhaps call your own console application.
Then you just need to add a file called "ProfileName.suricate-profile" to your
User folder containing the following

```json
{
  "user_commands":
  {
    "open_windows_terminal_here":
    {
      "keys": ["ctrl+shift+t"],
      "args": {"cmd": ["Console.exe", "-d", "${file_path}"]}
    }
  }
}
```

This overrides just the tags "keys" and "args", leaving the rest as define in
the original command.

### Platform Specific Tags

In order to make easier to implement platform specific variants of the same
command, individual command tags can be overridden adding the platform name as
extension. For instance, to add the Linux variant of the previous command we
could rewrite it as

```json
"open_terminal_here":
{
  "caption":      "Open Terminal Here...",
  "keys":         ["ctrl+o", "ctrl+t"],
  "flags":        "Windows|Linux|IsFile",
  "call":         "Suricate.lib.process.spawn",
  "args.windows": {"cmd": ["start", "cmd.exe"], "working_dir": "${file_path}"},
  "args.linux":   {"cmd": ["gnome-terminal"], "working_dir": "${file_path}"},
  "context_menu": true
}
```

This way all the command specifications are shared but the function call
arguments change based on the current platform, this way the same command
launches a different console application depending on the platform.

!!! tip
    For more details on how to write commands take a look at the
    [Default.suricate-profile] shipped with the Suricate package. See
    menu Preferences>Package Settings>Suricate>Default Profile - Default.

## Key bindings

There is still one common issue with the command above, the `ctrl` key in the
key binding is typically replaced by `super` (command key) in OSX. We could add
a "keys.osx" overriding the default keys but for this specific case another
method is preferred. By default, the special key `<c>` is remapped to `ctrl` in
Windows and Linux, and to `super` in OSX. This way the key binding in the
command above should be defined as `"keys": ["<c>+o", "<c>+t"]`. In fact, the
way keys are remapped can be completely customized in your settings file with
the "key_map" setting.

!!! warning
    By default most of the key bindings of the commands provided start with
    `<c>+o`, which interferes with Sublime Text's open file command. This
    behaviour can be changed tweaking the "override_default_opening_key" setting
    in your "User/Suricate.sublime-settings". For instance,
    `override_default_opening_key": "<c>+["` changes Suricate's key bindings as
    `<c>+o,<c>+p` to `<c>+[,<c>+p`.

    Alternatively, default key bindings can be ignored altogether adding
    `"ignore_default_keybindings": true` to your Suricate settings file.


[Sublime Text 3]: https://sublimetext.com/
[Default.suricate-profile]: https://raw.githubusercontent.com/nsubiron/SublimeSuricate/master/profiles/Default.suricate-profile
