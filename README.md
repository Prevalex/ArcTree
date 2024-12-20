# ArcTree

This utility allows you to archive all subfolders tree of the specified folder separately and save them in
specified folder as separate archives using PkZipc, Rar or 7ZIP

All archives will be stored in the specified destination path using the following naming convention:

Each archive name will consist of the archive folder name and path.

###For instance:

Suppose we archive subfolders of the folder e:\My Documents
Where are the subfolders:

e:\My Documents\Calcs  
e:\My Documents\Texts  
e:\My Documents\Photo  
e:\My Documents\Photo\JPG 

So the names of the resulting archives will be (assuming we use PkZipC):

 [My Documents][Calcs].zip  
 [My documents][Texts].zip  
 [My Documents][Photo].zip  
 [My Documents][Photo][JPG].zip  

 



