Quick Guide
===========

## Profiles

_Suricate Profiles_ are JSON files containing definitions of commands. A couple
of profiles come already shipped and active by default with Sublime Suricate. To
activate a profile add it to your **profile list** via _"Suricate: Add Profile"_
in the command palette (`ctrl+shift+p`), use _"Suricate: Remove Profile"_ to
deactivate profiles. Alternatively, you can edit your profile list by hand in
your `User/Suricate.sublime-settings`.

When a profile is active all the files matching `ProfileName.suricate-profile`
within your Packages directory are loaded (just as any other Sublime Text
settings file) and the Suricate merges their commands and adds them to you user
profile. To take a look at your user profile use _"Suricate: View Profiles"_.
This generates a  list of your active commands as well as lists for each
individual profile found in your directory tree. However, the commands  active
in your user profile are not necessarily available. Whether or not a command can
be used depends on the set of flags given by the command itself, these flags are
updated in a per-view basis.

To write your own profile take a look first to the `Default.suricate-profile` in
the menu Preferences>Package Settings>Suricate>Default Profile - Default.

## Commands

A typical Suricate command is defined as follows

```json
"open_windows_terminal_here":
{
  "caption":      "Open Terminal Here...",
  "keys":         ["ctrl+alt+t"],
  "group":        "launch",
  "flags":        "Windows|IsFile",
  "call":         "Suricate.lib.process.spawn",
  "args":         {"cmd": ["start", "cmd.exe"], "working_dir": "${file_path}"},
  "context_menu": true
}
```

This creates a command entry in the command palette, in the context menu and
assignates a key-binding to it. Moreover, the flags specify that the command is
only active on Windows and when the current buffer is a file existing on disk.

Any of the fields above can be overridden adding a suricate-profile file
to your User folder, e.g. let's say that the previous command resides in
`Default.suricate-profile` inside the Suricate package, and you want to assign a
different key-binding and perhaps call your own console application. Then you
just need to add a file called `Default.suricate-profile` to your User folder
containing the following

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

For more details on how this works take a look at the
`Default.suricate-profile`.

### Key bindings

**IMPORTANT:** By default most of the key bindings of the commands provided
start with `ctrl+o`, which interferes with Sublime Text's open file command. If
that poses a problem for you, you can change this behaviour tweaking
`"override_ctrl_o"` setting in your `User/Suricate.sublime-settings`. For
instance, `"override_ctrl_o": "ctrl+["` changes Suricate's key bindings as
`ctrl+o,ctrl+p` to `ctrl+[,ctrl+p`.

Alternatively, default key bindings can be ignored altogether adding
`"ignore_default_keybindings": true` to your Suricate settings file.
