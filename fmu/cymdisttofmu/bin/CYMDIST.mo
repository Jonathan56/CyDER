model CYMDIST
  "Block that exchanges a vector of real values with CYMDIST"
  extends Modelica.Blocks.Interfaces.BlockIcon;
  
///////////// THE CODE BELOW HAS BEEN AUTOGENERATED //////////////
  Modelica.Blocks.Interfaces.RealInput VMAG_A(start=0.0, unit="V")
    "VMAG_A" annotation(Placement(transformation(extent={{-122,68},{-100,90}})));
  Modelica.Blocks.Interfaces.RealInput VMAG_B(start=0.0, unit="V")
    "VMAG_B" annotation(Placement(transformation(extent={{-122,48},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput VMAG_C(start=0.0, unit="V")
    "VMAG_C" annotation(Placement(transformation(extent={{-122,28},{-100,50}})));
  Modelica.Blocks.Interfaces.RealInput VANG_A(start=0.0, unit="deg")
    "VANG_A" annotation(Placement(transformation(extent={{-122,8},{-100,30}})));
  Modelica.Blocks.Interfaces.RealInput VANG_B(start=-120.0, unit="deg")
    "VANG_B" annotation(Placement(transformation(extent={{-122,-12},{-100,10}})));
  Modelica.Blocks.Interfaces.RealInput VANG_C(start=120.0, unit="deg")
    "VANG_C" annotation(Placement(transformation(extent={{-122,-32},{-100,-10}})));
  Modelica.Blocks.Interfaces.RealOutput IA (unit="A")
    "IA" annotation(Placement(transformation(extent={{100,70},{120,90}})));
  Modelica.Blocks.Interfaces.RealOutput IB (unit="A")
    "IB" annotation(Placement(transformation(extent={{100,52},{120,72}})));
  Modelica.Blocks.Interfaces.RealOutput IC (unit="A")
    "IC" annotation(Placement(transformation(extent={{100,34},{120,54}})));
  Modelica.Blocks.Interfaces.RealOutput IAngleA (unit="deg")
    "IAngleA" annotation(Placement(transformation(extent={{100,16},{120,36}})));
  Modelica.Blocks.Interfaces.RealOutput IAngleB (unit="deg")
    "IAngleB" annotation(Placement(transformation(extent={{100,-2},{120,18}})));
  Modelica.Blocks.Interfaces.RealOutput IAngleC (unit="deg")
    "IAngleC" annotation(Placement(transformation(extent={{100,-20},{120,0}})));
  
  parameter Real _saveToFile = 0 "Flag for writing results"; 
  parameter String _configurationFileName="" "Configuration file name";
protected   
  parameter Integer nDblPar=0 
    "Number of double parameter values to sent to CYMDIST";
  parameter Integer nDblInp(min=1)=6 
    "Number of double input values to sent to CYMDIST";
  parameter Integer nDblOut(min=1)=6  
    "Number of double output values to receive from CYMDIST";
 
  Real resWri[1]= {_saveToFile} "Flag for writing results";
  Real dblInpVal[nDblInp] "Value to be sent to CYMDIST";
  
  
  Real uR[nDblInp]={
  VMAG_A,
  VMAG_B,
  VMAG_C,
  VANG_A,
  VANG_B,
  VANG_C 
  }"Variables used to collect values to be sent to CYMDIST";
   
  Real yR[nDblOut]={
  IA,
  IB,
  IC,
  IAngleA,
  IAngleB,
  IAngleC 
  }"Variables used to collect values received from CYMDIST";
  
  parameter String dblInpNam[nDblInp]={
  "VMAG_A",
  "VMAG_B",
  "VMAG_C",
  "VANG_A",
  "VANG_B",
  "VANG_C" 
  }"Input variables names to be sent to CYMDIST";
  
  parameter String dblOutNam[nDblOut]={
  "IA",
  "IB",
  "IC",
  "IAngleA",
  "IAngleB",
  "IAngleC" 
  }"Output variables names to be received from CYMDIST";
  parameter String dblParNam[nDblPar](each start="") 
    "Parameter variables names to be sent to CYMDIST";
  parameter Real dblParVal[nDblPar]=zeros(nDblPar)
    "Parameter variables values to be sent to CYMDIST";
  
///////////// THE CODE ABOVE HAS BEEN AUTOGENERATED //////////////  
  
  parameter String moduleName="fmu"
    "Name of the python module that contains the function";
  parameter String functionName="cymdist" 
    "Name of the python function";
  
initial equation 
  assert(_configurationFileName <> "",
    "Parameter _configurationFileName: " +
     _configurationFileName + " must be set to " +
     "the path to the JSON configuration file. " +
     "This must be done prior to entering the " +
     "initialization mode of the FMU.");
equation 
  // Compute values that will be sent to CYMDIST
  for i in 1:nDblInp loop
	dblInpVal[i] = uR[i];
  end for;
  
  // Exchange data
  yR = CYMDISTToFMU.Python34.Functions.cymdist(
	  moduleName=moduleName,
	  functionName=functionName,
	  conFilNam=_configurationFileName,
	  modTim={time},
	  nDblInp=nDblInp,
	  dblInpNam=dblInpNam,
	  dblInpVal=dblInpVal,
	  nDblOut=nDblOut,
	  dblOutNam=dblOutNam,
	  nDblPar=nDblPar,
	  dblParNam=dblParNam,
	  dblParVal=dblParVal,
	  resWri=resWri);    
end CYMDIST;