# ZSH completions for LbEnv and LbDevTools

## Basic functionality

zsh tab completion works by providing a couple of shell functions, typically
named `_CMD` for the completion of the command `CMD`.

These are shipped through the `$FPATH`/`$fpath` (function path) variable: Each
file in every directory in the `FPATH` becomes a function when a shell is
started and the function name is the file's name. I.e. a file named `_lb-run`
causes a function `_lb-run` to be defined. Functions normally become attributed
to completions by calling `compinit`, it is usually in a user's `$HOME/.zshrc`
file.

Tab completion for LbEnv et al is thus shipped to the user by providing the
`/cvmfs/lhcb.cern.ch/lib/var/lib/LbEnv/stable/x86_64-centos7/share/zsh/completions/`
directory. It has been decided not to interfer with users' setups by default,
and it is therefore up to a user to add this directory to their `$FPATH` before
calling `compinit`.

## Steps neccessary on the user side to use completions

### Option 1: Setting FPATH in zshrc
The most straight forward way would be editing the `$HOME/.zshrc` file.  Note
that the `FPATH` exists as colon-separated string (`$FPATH`) and as array
variable (`$fpath`)
```sh
# somewhere in .zshrc
fpath+=(/cvmfs/lhcb.cern.ch/lib/var/lib/LbEnv/stable/x86_64-centos7/share/zsh/completions/)
compinit
```

If a user doesn't set up LbEnv in their `.zshrc` file, this isn't ideal:
This has the disadvantage of the hard coded path in the `.zshrc` file that gets
(potentially) invoked before a user decided against using the production
version of LbEnv, maybe doesn't use LbEnv at all, uses LbEnv on a different
platform (slc6?).

### Option 2: Setting FPATH and calling compinit manually every time.

One can manipulated the `FPATH` after setting LbEnv up **interactively**:

```sh
fpath+=($(dirname =lb-dev)/../share/zsh/completions)
compinit
```

This option is obviously inconvenient as one has to perform these steps in
every new shell. Furthermore it invalidates the completion cache that a user
may have every time these steps are performed and every time a new shell gets
started!

### Option 3: Using the helper script

After sourcing `/cvmfs/lhcb.cern.ch/lib/LbEnv-stable.sh` one can source the
`zsh_completion` helper:

```sh
source /cvmfs/lhcb.cern.ch/lib/LbEnv-stable.sh
source $(dirname =lb-dev)/../share/zsh/zsh_completion
```
The helper attempts to be as minimal invasive as possible. It does not call
`compinit` and thus avoids:
 * avoids problems with calling `compinit` differently than the user
 * does not invalidate the completion cache

It does so by manipulating the `_comps` variable.

The disadvantage is that it's a rather involved script and thus probably error
prone.

## Customization

The style `':completion::complete:lb-run::' fake-commands` sets up commands
that are completed after `lb-run` even if they are not currently executable.
This can be useful for e.g. gaudirun.py in `lb-run DaVinci gaud<TAB>`. An
example for a user's zshrc is:

```sh
zstyle ':completion::*:lb-run::' fake-commands gaudirun.py bender db-tags
```

If this is **not** set, then the completion on `lb-run DaVinci <TAB>` will just
suggest currently executable commands, i.e. outside the `lb-run` environment.
**With** the example setting, the completion will also suggest `gaudirun.py`,
`bender`, and `db-tags`.
