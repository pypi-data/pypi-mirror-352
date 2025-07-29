###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

# Note: we want the user commands to be things like `lb-set-platform`, but `-`
# is not allowed as function name by all sh implementations
# (http://cern.ch/go/F7Dk), so we use a valid function name, but then we use an
# alias to expose to users the desired name (which in principle should not be
# allowed either, but all implementations I could try are happy enough with it)

lb_set_platform() {
  if [ "$#" -ne 1 ]; then
    echo "usage: lb-set-platform <platform>"
    return 2
  fi
  # TODO check if argument is a valid platform
  export BINARY_TAG="$1"
  export CMTCONFIG="$1"
}
alias lb-set-platform=lb_set_platform

# make sure old LbScripts alias does not interfere
unalias LbLogin >/dev/null 2>&1 || true
LbLogin() {
  if [ "$1" = "-c" ] ; then
    echo "'LbLogin -c' is deprecated, use 'lb-set-platform $2'"
    lb-set-platform "$2"
  else
    echo "error: invalid arguments: only -c option is supported"
    return 1
  fi
}

lb_set_workspace() {
  local old="$CMAKE_PREFIX_PATH"
  if [ -n "$1" ] ; then
    local ws=$(cd "$1" && pwd)
  else
    local ws=
  fi
  export CMAKE_PREFIX_PATH="$ws":$(printenv -0 CMAKE_PREFIX_PATH | tr : \\0 | grep -vzxF "$LBENV_CURRENT_WORKSPACE" | tr \\0 :)
  export CMAKE_PREFIX_PATH=$(printenv CMAKE_PREFIX_PATH | sed 's/^:*//;s/:*$//')
  export LBENV_CURRENT_WORKSPACE="$ws"
  if [ "$CMAKE_PREFIX_PATH" != "$old" ] ; then
    echo "new CMAKE_PREFIX_PATH is:"
    printenv CMAKE_PREFIX_PATH | tr : \\n | sed "s/^/  /"
  else
    echo "no change to CMAKE_PREFIX_PATH needed"
  fi
}
alias lb-set-workspace=lb_set_workspace

if [ -n "${BASH_VERSION:-}" -a -n "${VIRTUAL_ENV:-}" ] ; then
  lb_enable_shell_completion() {
    source "$VIRTUAL_ENV/share/bash-completion/bash_completion"
  }
  alias lb-enable-shell-completion=lb_enable_shell_completion
fi

if [ -n "${ZSH_VERSION:-}" -a -n "${VIRTUAL_ENV:-}" ] ; then
  lb_enable_shell_completion() {
    source "$VIRTUAL_ENV/share/zsh/zsh_completion"
  }
  alias lb-enable-shell-completion=lb_enable_shell_completion
fi
