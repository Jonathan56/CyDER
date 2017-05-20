within CYMDISTToFMU.Python34.Functions;
function cymdist "Function that communicates with the CYMDISTToFMU Python API"
  extends Modelica.Icons.Function;
  input String moduleName
  "Name of the python module that contains the function";
  input String functionName=moduleName "Name of the python function";
  input String  conFilNam "Name of the python function";
  input Real    modTim[1] "Model time";
  input Real    dblParVal[nDblPar] "Parameter variables values to send to CYMDISTToFMU";
  input Real    dblInpVal[max(1, nDblInp)] "Input variables values to be sent to CYMDISTToFMU";
  input String  dblParNam[nDblPar] "Parameter variables names to send to CYMDISTToFMU";
  input String  dblOutNam[max(1, nDblOut)] "Output variables names to be read from CYMDISTToFMU";
  input String  dblInpNam[max(1, nDblInp)] "Input variables names to be sent to CYMDISTToFMU";
  input Integer nDblInp(min=0) "Number of double inputs to send to CYMDISTToFMU";
  input Integer nDblOut(min=0) "Number of double outputs to read from CYMDISTToFMU";
  input Integer nDblPar(min=0) "Number of double parameters to send to CYMDISTToFMU";
  input Real    resWri[1]  "Flag for enabling results writing. 1: write results, 0: else";
  output Real dblOutVal[max(1, nDblOut)] "Double output values read from CYMDISTToFMU";
algorithm
  // Call the exchange function
dblOutVal := BaseClasses.cymdist(
      moduleName=moduleName,
      functionName=functionName,
      conFilNam=conFilNam,
      modTim=modTim,
      nDblInp=nDblInp,
      dblInpNam=dblInpNam,
      dblInpVal=dblInpVal,
      nDblOut=nDblOut,
      dblOutNam=dblOutNam,
      nDblPar=nDblPar,
      dblParNam=dblParNam,
      dblParVal=dblParVal,
      resWri=resWri);
annotation (Documentation(info="<html>
<p>
This function is a wrapper for 
<a href=\"modelica://CYMDISTToFMU.Python34.Functions.BaseClasses.cymdist\">
CYMDISTToFMU.Python34.Functions.BaseClasses.cymdist</a>.
It adds the directory <code>modelica://CYMDISTToFMU/Resources/Python-Sources</code>
to the environment variable <code>PYTHONPATH</code>
prior to calling the function that exchanges data with Python.
After the function call, the <code>PYTHONPATH</code> is set back to what
it used to be when entering this function.
See 
<a href=\"modelica://CYMDISTToFMU.Python34.UsersGuide\">
CYMDISTToFMU.Python34.UsersGuide</a>
for instructions, and 
<a href=\"modelica://CYMDISTToFMU.Python34.Functions.Examples\">
CYMDISTToFMU.Python34.Functions.Examples</a>
for examples.
</p>
</html>",
        revisions="<html>
<ul>
<li>
October 17, 2016, by Thierry S. Nouidui:<br/>
First implementation.
</li>
</ul>
</html>"));
end cymdist;
