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
alias lb-set-platform 'setenv BINARY_TAG "\!:1" ; setenv CMTCONFIG "\!:1"'

alias LbLogin 'echo "'"'LbLogin -c'"'" is deprecated, use "'"'lb-set-platform \!:2'"'" ; lb-set-platform "\!:2"'

alias lb-set-platform 'setenv BINARY_TAG "\!:1" ; setenv CMTCONFIG "\!:1"'

alias lb-set-workspace 'set _ws = `cd \!:1 && pwd` ; setenv CMAKE_PREFIX_PATH `( echo "$_ws" ; printenv CMAKE_PREFIX_PATH | tr : \\n | grep -vxF "$LBENV_CURRENT_WORKSPACE" ) | tr \\n :` ; setenv CMAKE_PREFIX_PATH `printenv CMAKE_PREFIX_PATH | sed '"'"'s/^:*//;s/:*$//'"'"'` ; setenv LBENV_CURRENT_WORKSPACE "$_ws" ; unset _ws ; echo "current CMAKE_PREFIX_PATH is:" ; printenv CMAKE_PREFIX_PATH | tr : \\n | sed "s/^/  /"'
