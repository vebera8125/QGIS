############################### reg2nsis begin #################################
# This NSIS-script was generated by the Reg2Nsis utility                       #
# Author  : Artem Zankovich                                                    #
# URL     : http://aarrtteemm.nm.ru                                            #
# Usage   : You can freely inserts this into your setup script as inline text  #
#           or include file with the help of !include directive.               #
#           Please don't remove this header.                                   #
################################################################################

WriteRegStr HKEY_CURRENT_USER "Software\QGIS\QGIS3\Plugins" "grassplugin" "true"
WriteRegStr HKEY_CURRENT_USER "Software\QGIS\QGIS3\Plugins" "offlineeditingplugin" "true"
WriteRegStr HKEY_CURRENT_USER "Software\QGIS\QGIS3\Plugins" "topolplugin" "true"

###############################  reg2nsis end  #################################
