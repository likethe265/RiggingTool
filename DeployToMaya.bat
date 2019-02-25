@echo off
SET dic=C:\Users\Administrator.DESKTOP-IIFPKMS\Documents\maya\2017\plug-ins
copy ".\MatrixCombine.py" %dic%"\MatrixCombine.py" 
copy ".\rbfBlender.py" %dic%"\rbfBlender.py" 
copy ".\SampleValueBlender.py" %dic%"\SampleValueBlender.py" 
copy ".\PoseWeightSolver.py" %dic%"\PoseWeightSolver.py" 
copy ".\FacialControllerConstraint.py" %dic%"\FacialControllerConstraint.py" 
copy ".\SampleValueOut.py" %dic%"\SampleValueOut.py" 
@echo deploy finished, press any key to close the window.
pause