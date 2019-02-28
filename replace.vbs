Dim oRegExp
Dim strPattern, strReplace, strResult
Const ForReading = 1    
Const ForWriting = 2

strFileName = Wscript.Arguments(0)
strDic = Wscript.Arguments(1)

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.OpenTextFile(strFileName, ForReading)
strText = objFile.ReadAll
objFile.Close

strPattern = "rootDic[ =':\/\\\w.]*"
strReplace = "rootDic = '" + strDic +"'"
Set oRegExp = New RegExp
oRegExp.Pattern = strPattern
strResult = oRegExp.Replace(strText, strReplace)

Set objFile = objFSO.OpenTextFile(strFileName, ForWriting)
objFile.Write strResult  'WriteLine adds extra CR/LF
objFile.Close